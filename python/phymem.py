# This is the only file you must implement

# This file will be imported from the main code. The PhysicalMemory class
# will be instantiated with the algorithm received from the input. You may edit
# this file as you which

# NOTE: there may be methods you don't need to modify, you must decide what
# you need...

from Queue import Queue


class PhysicalMemory:
    ALGORITHM_AGING_NBITS = 8
    """How many bits to use for the Aging algorithm"""

    def __init__(self, algorithm):
        assert algorithm in {"fifo", "nru", "aging", "second-chance"}
        self.algorithm = algorithm

        if algorithm == "fifo":
            self.impl = FIFOAlgorithm()
        elif algorithm == "second-chance":
            self.impl = SecondChanceAlgorithm()

    def put(self, frameId):
        """Allocates this frameId for some page"""
        # Notice that in the physical memory we don't care about the pageId, we only
        # care about the fact we were requested to allocate a certain frameId
        self.impl.put(frameId)


    def evict(self):
        """Deallocates a frame from the physical memory and returns its frameId"""
        # You may assume the physical memory is FULL so we need space!
        # Your code must decide which frame to return, according to the algorithm
        return self.impl.evict()

    def clock(self):
        """The amount of time we set for the clock has passed, so this is called"""
        # Clear the reference bits (and/or whatever else you think you must do...)
        self.impl.clock()

    def access(self, frameId, isWrite):
        """A frameId was accessed for read/write (if write, isWrite=True)"""
        self.impl.access(frameId, isWrite)


class FIFOAlgorithm:
    def __init__(self):
        self.allocatedFrames = Queue()

    def put(self, frameId):
        """Allocates this frameId for some page"""
        # Notice that in the physical memory we don't care about the pageId, we only
        # care about the fact we were requested to allocate a certain frameId
        self.allocatedFrames.put(frameId)
        pass

    def evict(self):
        """Deallocates a frame from the physical memory and returns its frameId"""
        # You may assume the physical memory is FULL so we need space!
        # Your code must decide which frame to return, according to the algorithm
        return self.allocatedFrames.get()

    def clock(self):
        """The amount of time we set for the clock has passed, so this is called"""
        # Clear the reference bits (and/or whatever else you think you must do...)
        pass

    def access(self, frameId, isWrite):
        """A frameId was accessed for read/write (if write, isWrite=True)"""
        pass


class SecondChanceAlgorithm:
    def __init__(self):
        self.allocatedFrames = []

    def put(self, frameId):
        """Allocates this frameId for some page"""
        # Notice that in the physical memory we don't care about the pageId, we only
        # care about the fact we were requested to allocate a certain frameId
        # [frameId, R-bit]
        self.allocatedFrames.append([frameId, 0])
        pass

    def evict(self):
        """Deallocates a frame from the physical memory and returns its frameId"""
        # You may assume the physical memory is FULL so we need space!
        # Your code must decide which frame to return, according to the algorithm
        while True:
            frame = self.allocatedFrames.pop(0)
            if frame[1] == 0:
                return frame[0]
            else:
                frame[1] = 0
                self.allocatedFrames.append(frame)

    def clock(self):
        """The amount of time we set for the clock has passed, so this is called"""
        # Clear the reference bits (and/or whatever else you think you must do...)
        pass

    def access(self, frameId, isWrite):
        """A frameId was accessed for read/write (if write, isWrite=True)"""
        for i in xrange(len(self.allocatedFrames)):
            if self.allocatedFrames[i][0] == frameId:
                self.allocatedFrames[i][1] = 1
                break
