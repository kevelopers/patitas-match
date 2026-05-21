import sys
import logging
from tests.test_match_flow import execute_simulation
from tests.test_rescue_ai_flow import execute_ai_simulation

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def monitor_pipeline_execution() -> None:
    logger.info("====================================================")
    logger.info("STARTING PATITAMATCH CENTRALIZED TEST SUITE RUNNER")
    logger.info("====================================================")

    try:
        logger.info("MODULE 1: Executing Algorithmic Affinity Stack Flow Tests...")
        execute_simulation()
        logger.info("RESULT: Module 1 executed successfully without regressions.")

        logger.info("----------------------------------------------------")

        logger.info(
            "MODULE 2: Executing Multimodal Abstract Vision AI Pipeline Tests..."
        )
        execute_ai_simulation()
        logger.info("RESULT: Module 2 executed successfully without regressions.")

        logger.info("====================================================")
        logger.info("SUCCESS: Entire system suite successfully validated.")
        logger.info("====================================================")

    except Exception as error:
        logger.error("====================================================")
        logger.error(f"CRITICAL REGRESSION DETECTED: Suite execution halted.")
        logger.error(f"Details: {error}")
        logger.error("====================================================")
        sys.exit(1)


if __name__ == "__main__":
    monitor_pipeline_execution()
