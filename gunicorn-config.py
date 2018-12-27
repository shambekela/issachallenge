from app import scheduler

def when_ready(server):
	server.log.info("Server is ready. Spawning workers")