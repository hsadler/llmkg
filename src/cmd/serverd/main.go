package main

import (
	"context"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
	"github.com/rs/zerolog/log"

	"example-server/internal/dependencies"
	"example-server/internal/logger"
	"example-server/internal/openapi"
	"example-server/internal/openapi/ogen"
)

func main() {
	// Initialize logger
	logger.SetupGlobalLogger()

	// Create context that listens for the interrupt signal from the OS
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	// Setup dependencies
	neo4jDriver, _ := neo4j.NewDriverWithContext(
		os.Getenv("NEO4J_URI"),
		neo4j.BasicAuth(os.Getenv("NEO4J_USER"), os.Getenv("NEO4J_PASSWORD"), ""),
	)
	deps := dependencies.NewDependencies(
		neo4jDriver,
	)
	defer deps.CleanupDependencies()

	// Get port from environment or use default
	port := os.Getenv("PORT")
	if port == "" {
		port = "8000"
	}

	// Create OGEN server for LLMKG API
	llmkgOgenServer, err := ogen.NewServer(&openapi.LLMKGService{Deps: deps})
	if err != nil {
		log.Fatal().Err(err).Msg("Failed to create OGEN server")
	}

	// Create HTTP server for LLMKG API
	llmkgHttpServer := &http.Server{
		Addr:    fmt.Sprintf(":%s", port),
		Handler: llmkgOgenServer,
	}

	// Start items API server in a goroutine
	go func() {
		log.Info().Str("port", port).Msg("Starting server")
		if err := llmkgHttpServer.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatal().Err(err).Msg("Failed to start server")
		}
	}()

	// Wait for interrupt signal
	<-ctx.Done()
	log.Info().Msg("Shutting down server...")

	// Create a deadline to wait for
	shutdownCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// Shutdown server gracefully
	if err := llmkgHttpServer.Shutdown(shutdownCtx); err != nil {
		log.Fatal().Err(err).Msg("Server forced to shutdown")
	}

	log.Info().Msg("Server exited properly")
}
