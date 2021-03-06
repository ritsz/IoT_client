#! /usr/bin/env python

import os               
import sys              
import resource
from threading import Thread
import websocket_client
import cookielib
import urllib2
#import collector


aws_url = "http://52.74.92.28/"
plimmer_id = "Plimmer-2014100003"
session_save_url = aws_url+"sessionsave/"+plimmer_id
update_url = aws_url+"update"
server_post_url = aws_url+"tunnelresponse"
ws_url = "ws://52.74.92.28/ws/foobar?subscribe-session"
session_cookies = ""
database = "/www/user/data.db"



UMASK = 0
WORKDIR = "/"
MAXFD = 1024

if (hasattr(os, "devnull")):
	REDIRECT_TO = os.devnull
else:
	REDIRECT_TO = "/dev/null"

def createDaemon():
	try:
        	pid = os.fork()
   	except OSError, e:
      		raise Exception, "%s [%d]" % (e.strerror, e.errno)

   	if (pid == 0):	# The first child.
      		os.setsid()
       		try:
               		pid = os.fork()	# Fork a second child.
      		except OSError, e:
         		raise Exception, "%s [%d]" % (e.strerror, e.errno)

      		if (pid == 0):	# The second child.
         		os.umask(UMASK)
      		else:
               		os._exit(0)	# Exit parent (the first child) of the second child.
   	else:
      		os._exit(0)	# Exit parent of the first child.

   	
   	maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
   	if (maxfd == resource.RLIM_INFINITY):
      		maxfd = MAXFD
  
   	for fd in range(0, maxfd):
      		try:
         		#os.close(fd)
         		pass
      		except OSError:	# ERROR, fd wasn't open to begin with (ignored)
         		pass

   
   	#os.open(REDIRECT_TO, os.O_RDWR)	# standard input (0)
   	#os.dup2(0, 1)			# standard output (1)
   	#os.dup2(0, 2)			# standard error (2)

   	return(0)




def websocket_fn():
	try:
		websocket_client.main_thread(session_cookies, plimmer_id, ws_url, server_post_url)
	except:
		print "THE ERROR IS IN DAEMON"
		raise





def daemon_main(plim_id = None):
	if plim_id != None:
		plimmer_id = plim_id
		

	retCode = createDaemon()

        cookies = cookielib.LWPCookieJar()
        handlers = [
                urllib2.HTTPHandler(),
                urllib2.HTTPSHandler(),
                urllib2.HTTPCookieProcessor(cookies)
        ]
        opener = urllib2.build_opener(*handlers)
        req = urllib2.Request(session_save_url)
        print opener.open(req).read()



        for cookie in cookies:
                session_cookies = cookie
                print cookie.name, cookie.value


        try:
                thread1 = Thread(target=websocket_client.main_thread, args=(session_cookies, plimmer_id, ws_url, server_post_url,) )
                #thread2 = Thread(target=collector.main_thread, args=(session_cookies, plimmer_id, database, update_url,) )

                thread1.start()
                #thread2.start()
                
                thread1.join()
                # We don't wait on collector thread. If websocket thread fails, daemon has to be
                # restarted. Hence wait on collector is not required.
                #thread2.join()
        except Exception as e:
                print "EXCEPTION ON DAEMON", e
                raise

  

        sys.exit(retCode)

		
	




if __name__ == "__main__":
	daemon_main()
