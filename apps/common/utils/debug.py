import time                                                                     
                                                                                
def writelog(path, msg):                                                        
    f = open(path, "a+")                                                        
    line = "[%s] %s\n" % (time.asctime(), msg)                                  
    f.write(line)                                                               
    f.close()  


class Timer(object):
    """ measures the time elapsed since start_time and stop_time """

    def start(self):
        self.start_time = time.time()

    def stop(self):
        self.stop_time = time.time()

    def time_in_seconds(self):
        return str(self.stop_time - self.start_time) + ' s'

    def write_to_log(self, path, msg):
        msg = msg + ' ' + self.time_in_seconds()
        writelog(path, msg)
