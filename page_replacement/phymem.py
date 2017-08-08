# This is the only file you must implement

# This file will be imported from the main code. The PhysicalMemory class
# will be instantiated with the algorithm received from the input. You may edit
# this file as you which

# NOTE: there may be methods you don't need to modify, you must decide what
# you need...

from Queue import Queue

ALGORITHM_AGING_NBITS = 8


class PhysicalMemory:
    """How many bits to use for the Aging algorithm"""

    def __init__(self, algorithm):
        assert algorithm in {"fifo", "second-chance", "lru", "nru", "aging"}
        if algorithm == "fifo":
            self.algorithm = FifoPhysicalMemory()
        elif algorithm == "second-chance":
            self.algorithm = SecondChancePhysicalMemory()
        elif algorithm == "aging":
            self.algorithm = AgingPhysicalMemory()
        elif algorithm == "nru":
            self.algorithm = NRUPhysicalMemory()
        elif algorithm == "lru":
            self.algorithm = LRUPhysicalMemory()

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
        self.allocatedFrames = Queue()

    def put(self, frameId):
        self.allocatedFrames.put(frameId)

    def evict(self):
        return self.allocatedFrames.get()

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
        for frame in self.allocatedFrames:
            if frame[0] == frameId:
                return

        self.allocatedFrames.append([frameId, 1])

    def evict(self):
        while True:
            frame = self.allocatedFrames.pop(0)
            if frame[1] == 0:
                return frame[0]
            else:
                frame[1] = 0
                self.allocatedFrames.append(frame)

    def clock(self):
        pass

    def access(self, frameId, isWrite):
        for frame in self.allocatedFrames:
            if frame[0] == frameId:
                frame[1] = 1  # referenced
                break


class LRUPhysicalMemory(object):
    """
      In the LRU algorithm the page frame is represented
      as a list of lists [x, y].
      x --> frameId
      y --> counter
    """

    def __init__(self):
        self.allocatedFrames = []

    def put(self, frameId):
        self.allocatedFrames.append([frameId, 1])

    def evict(self):
        evicted_index = 0
        for index in xrange(1, len(self.allocatedFrames)):
            if self.allocatedFrames[index][1] < self.allocatedFrames[evicted_index][1]:
                evicted_index = index

        return self.allocatedFrames.pop(evicted_index)[0]

    def clock(self):
        pass

    def access(self, frameId, isWrite):
        for frame in self.allocatedFrames:
            if frame[0] == frameId:
                frame[1] += 1  # referenced
                break


class AgingPhysicalMemory(object):
    """
      In the aging algorithm the page frame is represented
      as list of lists [x, y, z].
      x --> frameId
      y --> bit R
      z --> aging counter
    """

    def __init__(self):
        global ALGORITHM_AGING_NBITS

        self.counter_bits = ALGORITHM_AGING_NBITS
        self.allocatedFrames = []

    def put(self, frameId):
        self.allocatedFrames.append([frameId, 1, 2 ** (self.counter_bits - 1)])

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
                frame[2] |= 2 ** (self.counter_bits - 1)

            frame[1] = 0  # Set referenced to zero

    def access(self, frameId, isWrite):
        for frame in self.allocatedFrames:
            if frame[0] == frameId:
                frame[1] = 1  # referenced


def nru_frameclass(frame):
    """
    3. referenced, modified
    2. referenced, not modified
    1. not referenced, modified
    0. not referenced, not modified

    index 1 --> referenced bit
    index 2 --> modified bit
    """
    if frame[1] == 1 and frame[2] == 1: return 3
    if frame[1] == 1 and frame[2] == 0: return 2
    if frame[1] == 0 and frame[2] == 1: return 1
    if frame[1] == 0 and frame[2] == 0: return 0


class NRUPhysicalMemory(object):
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
        self.allocatedFrames.append([frameId, 1, 0])

    def evict(self):
        frame_classes = map(nru_frameclass, self.allocatedFrames)

        min_class = 4
        min_index = -1

        for i in xrange(len(frame_classes)):
            if frame_classes[i] < min_class:
                min_index = i
                min_class = frame_classes[i]

        evict_frame = self.allocatedFrames.pop(min_index)

        return evict_frame[0]

    def clock(self):
        for frame in self.allocatedFrames:
            frame[1] = 0

    def access(self, frameId, isWrite):
        for frame in self.allocatedFrames:
            if frame[0] == frameId:
                frame[1] = 1
                if isWrite:
                    frame[2] = 1
