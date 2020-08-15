from backtest.strategies.pullback_entry import PullbackEntry
from backtest.dashboard import app

from backtest.util import settings as SETTINGS
from backtest.util import tools as TOOLS
import backtest.util.logger as LOGGER

from threading import Thread


if __name__ == "__main__":
    
	try:
		logger = LOGGER.setup_logger()
	# 	# TOOLS.create_dirs()
	
		Thread(target=app.run_server).start()

		app.run_server()

	except (KeyboardInterrupt, SystemExit):
		print('Fudeu lele')