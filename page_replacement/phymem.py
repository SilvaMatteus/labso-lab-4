# This is the only file you must implement

# This file will be imported from the main code. The PhysicalMemory class
# will be instantiated with the algorithm received from the input. You may edit
# this file as you which

# NOTE: there may be methods you don't need to modify, you must decide what
# you need...

class PhysicalMemory:
    ALGORITHM_AGING_NBITS = 8
    """How many bits to use for the Aging algorithm"""

    def __init__(self, algorithm):
        assert algorithm in {"fifo", "nru", "aging", "second-chance"}
        if algorithm == "fifo":
            self.algorithm = FifoPhysicalMemory()
        elif algorithm == "second-chance":
            self.algorithm = SecondChancePhysicalMemory()
        elif algorithm == "aging":
            self.algorithm = AgingPhysicalMemory()
            # Todo: add new algoritms

    def put(self, frameId):
        """Allocates this frameId for some page"""
        # Notice that in the physical memory we don't care about the pageId, we only
        # care about the fact we were requested to allocate a certain frameId
        self.algorithm.put(frameId)

    def evict(self):
        """Deallocates a frame from the physical memory and returns its frameId"""
        # You may assume the physical memory is FULL so we need space!
        # Your code must decide which frame to return, according to the algorithm
        return self.algorithm.evict()

    def clock(self):
        """The amount of time we set for the clock has passed, so this is called"""
        # Clear the reference bits (and/or whatever else you think you must do...)
        self.algorithm.clock()

    def access(self, frameId, isWrite):
        """A frameId was accessed for read/write (if write, isWrite=True)"""
        self.algorithm.access(frameId, isWrite)


class FifoPhysicalMemory(object):
    def __init__(self):
        self.allocatedFrames = []

    def put(self, frameId):
        self.allocatedFrames.append(int(frameId))

    def evict(self):
        return self.allocatedFrames.pop(0)

    def clock(self):
        pass

    def access(self, frameId, isWrite):
        pass


class SecondChancePhysicalMemory(object):
    """
      In the second chance algorithm the page frame is represented
      as a list of lists [x, y].
      x --> frameId
      y --> bit R
    """

    def __init__(self):
        self.allocatedFrames = []

    def put(self, frameId):
        self.allocatedFrames.append([int(frameId), 0])

    def evict(self):
        if self.allocatedFrames[0][1] == 0:
            return self.allocatedFrames.pop(0)[0]
        else:
            self.allocatedFrames.append(self.allocatedFrames.pop(0))
            self.allocatedFrames[-1][1] = 0
            for index in xrange(len(self.allocatedFrames)):
                if self.allocatedFrames[index][1] == 0:
                    return self.allocatedFrames.pop(index)[0]

    def clock(self):
        pass

    def access(self, frameId, isWrite):
        for frame in self.allocatedFrames:
            if frame[0] == frameId:
                frame[1] = 1  # referenced


class AgingPhysicalMemory(object):
    """
      In the aging algorithm the page frame is represented
      as list of lists [x, y, z].
      x --> frameId
      y --> bit R
      z --> aging counter
    """

    def __init__(self):
        self.allocatedFrames = []

    def put(self, frameId):
        self.allocatedFrames.append([int(frameId), 0, 0])

    def evict(self):
        evicted_index = 0
        for index in xrange(1, len(self.allocatedFrames)):
            if self.allocatedFrames[index][2] < self.allocatedFrames[evicted_index][2]:
                evicted_index = index

        return self.allocatedFrames.pop(evicted_index)[0]

    def clock(self):
        for frame in self.allocatedFrames:
            frame[2] = frame[2] >> 1  # right shift
            if frame[1] == 1:
                frame[2] += 128  # 1000 0000
            frame[1] = 0  # Set referenced to zero

    def access(self, frameId, isWrite):
        for frame in self.allocatedFrames:
            if frame[0] == frameId:
                frame[1] = 1  # referenced


class NRU(object):
    """
    The not recently used (NRU) page replacement algorithm is an algorithm that favours keeping pages in memory that
    have been recently used. This algorithm works on the following principle: when a page is referenced, a referenced
    bit is set for that page, marking it as referenced. Similarly, when a page is modified (written to), a modified
    bit is set. The setting of the bits is usually done by the hardware, although it is possible to do so on the
    software level as well.

    At a certain fixed time interval, a timer interrupt triggers and clears the referenced bit of all the pages,
    so only pages referenced within the current timer interval are marked with a referenced bit. When a page needs
    to be replaced, the operating system divides the pages into four classes:

    3. referenced, modified
    2. referenced, not modified
    1. not referenced, modified
    0. not referenced, not modified
     
    Although it does not seem possible for a page to be not referenced yet modified, this happens when a class 3 page
    has its referenced bit cleared by the timer interrupt. The NRU algorithm picks a random page from the lowest
    category for removal. So out of the above four pages, the NRU algorithm will replace the not referenced, not 
    modified. Note that this algorithm implies that a modified but not referenced (within last timer interval) page is
    less important than a not modified page that is intensely referenced.
    
    The page frame is represented as list of lists [x, y, z].
      x --> frameId
      y --> referenced bit
      z --> modified bit
    """

    def __init__(self):
        self.allocatedFrames = []

    def put(self, frameId):
        self.allocatedFrames.append([int(frameId), 0, 0])

    def evict(self):
        evicted_index = 0
        for index in xrange(1, len(self.allocatedFrames)):
            if self.allocatedFrames[index][2] < self.allocatedFrames[evicted_index][2]:
                evicted_index = index

        return self.allocatedFrames.pop(evicted_index)[0]

    def clock(self):
        for frame in self.allocatedFrames:
            frame[2] = frame[2] >> 1  # right shift
            if frame[1] == 1:
                frame[2] += 128  # 1000 0000
            frame[1] = 0  # Set referenced to zero

    def access(self, frameId, isWrite):
        for frame in self.allocatedFrames:
            if frame[0] == frameId:
                frame[1] = 1  # referenced