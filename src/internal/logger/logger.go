package logger

import (
	"io"
	"os"

	"github.com/pkg/errors"
	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"
	"github.com/rs/zerolog/pkgerrors"
)

func SetupGlobalLogger() {
	l := getLoggingLevel()
	w := getWriter()
	zerolog.SetGlobalLevel(l)
	zerolog.ErrorStackMarshaler = pkgerrors.MarshalStack
	log.Logger = log.Output(w)
	log.Info().Msg("Logging setup complete")
}

func LogErrorWithStacktrace(err error, errMsg string) {
	log.Error().Stack().Err(errors.Wrap(err, errMsg)).Msg(errMsg)
}

func getWriter() io.Writer {
	if os.Getenv("IS_PROD") == "true" {
		return os.Stderr
	}
	return zerolog.ConsoleWriter{Out: os.Stderr}
}

func getLoggingLevel() zerolog.Level {
	if os.Getenv("IS_PROD") == "true" {
		return zerolog.InfoLevel
	}
	return zerolog.TraceLevel
}
