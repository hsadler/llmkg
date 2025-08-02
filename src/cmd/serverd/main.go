package main

import (
	"context"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/rs/zerolog/log"

	"example-server/internal/database"
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
	dbPool, _ := database.SetupDB()
	deps := dependencies.NewDependencies(
		dbPool,
	)
	defer deps.CleanupDependencies()

	// Get port from environment or use default
	port := os.Getenv("PORT")
	if port == "" {
		port = "8000"
	}

	// Create OGEN server for items API
	itemsOgenServer, err := ogen.NewServer(&openapi.ItemsService{Deps: deps})
	if err != nil {
		log.Fatal().Err(err).Msg("Failed to create OGEN server")
	}

	// Create HTTP server for items API
	itemsHttpServer := &http.Server{
		Addr:    fmt.Sprintf(":%s", port),
		Handler: itemsOgenServer,
	}

	// Start items API server in a goroutine
	go func() {
		log.Info().Str("port", port).Msg("Starting server")
		if err := itemsHttpServer.ListenAndServe(); err != nil && err != http.ErrServerClosed {
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
	if err := itemsHttpServer.Shutdown(shutdownCtx); err != nil {
		log.Fatal().Err(err).Msg("Server forced to shutdown")
	}

	log.Info().Msg("Server exited properly")
}
