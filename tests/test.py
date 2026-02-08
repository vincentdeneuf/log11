from log11 import get_logger

log = get_logger()

log.info("Application started")
log.warning("Low disk space")
log.error("Unhandled exception", a="test", b=123, c={"x": 456})