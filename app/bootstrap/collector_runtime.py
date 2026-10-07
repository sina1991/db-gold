import logging
import time

from app.collector import CollectorService
from app.config import COLLECTOR_POLL_SECONDS


logger = logging.getLogger(__name__)


class CollectorRuntime:
    def __init__(
        self,
        service: CollectorService | None = None,
        poll_seconds: int = COLLECTOR_POLL_SECONDS,
    ):
        self.service = service or CollectorService()
        self.poll_seconds = poll_seconds
        self.running = False

    def run_once(self) -> dict | None:
        return self.service.collect_latest_closed()

    def run(self) -> None:
        self.running = True

        try:
            while self.running:
                try:
                    candle = self.run_once()

                    if candle is not None:
                        logger.info(
                            "Collected closed candle: time=%s close=%s",
                            candle["time"],
                            candle["close"],
                        )

                except Exception:
                    logger.exception(
                        "Collector iteration failed"
                    )

                if self.running:
                    time.sleep(self.poll_seconds)

        except KeyboardInterrupt:
            logger.info("Collector runtime interrupted")

        finally:
            self.running = False

    def stop(self) -> None:
        self.running = False


def main() -> None:
    CollectorRuntime().run()


if __name__ == "__main__":
    main()
