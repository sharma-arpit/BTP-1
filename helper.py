import cv2
import numpy as np

# Structure for individual Face

class MFTracker_Face:

	def __init__(self, window=(-1, -1, -1, -1)):
		self.m_FaceGlobalID = -1                                               # Global ID
		self.m_FaceID = -1                                                     # FaceID in the Tracker List
		self.m_Face_Window = window                                      # Face Window tuple
		self.m_Face = None                                                     # Face image object
		self.m_FaceHSV = None
		self.m_HSVHist = None
		self.m_ColMatchVal = 1.0                                               # Color match Val at Tracked position
		self.m_FaceTracked = False                                             # True if Face is Well Tracked
		self.m_FaceWithinScene = False                                         # True if Face is Within Scene
		self.m_FaceDetectionState = 0                                          # Face detection State 0/1/2/3
		self.m_FaceDataReady = False
		self.m_TimeSpan_FaceTrackLoss = -1
		self.m_FaceIsolated = False


	def reset_mftrackerFace_Data(self):
		self.m_FaceGlobalID = -1
		self.m_FaceID = -1
		self.m_Face_Window = (-1, -1, -1, -1)
		self.m_FaceHSV = None
		self.m_Face = None
		self.m_HSVHist = None
		self.m_ColMatchVal = -1
		self.m_FaceTracked = False
		self.m_FaceIsolated = False
		self.m_FaceWithinScene = False
		self.m_FaceDetectionState = 0
		self.m_TimeSpan_FaceTrackLoss = -1
		self.m_FaceDataReady = False


	def set_mftrackerFace_Data(self, mftracker, detectedFaceCount, faceID):
		faceGlobalID = mftracker.GlobalNum
		frame = mftracker.CurrFrame
		window = mftracker.m_DetectedFace_WindowArray[ detectedFaceCount ]
		faceDetectionState = mftracker.m_DetectedFace_StateArray[ detectedFaceCount ]
		self.m_FaceDataReady = True
		self.m_FaceGlobalID = faceGlobalID
		self.m_FaceID = faceID
		self.m_Face_Window = window
		self.m_Face = frame[window[1]:window[1]+window[3], window[0]:window[0]+window[2]]
		self.m_FaceHSV = cv2.cvtColor(self.m_Face, cv2.COLOR_BGR2HSV)
		self.m_HSVHist = cv2.calcHist([self.m_FaceHSV], [0], None, [180], [0, 180])
		cv2.normalize(self.m_HSVHist, self.m_HSVHist, 0, 255, cv2.NORM_MINMAX)
		self.m_FaceTracked = True
		self.m_FaceIsolated = True
		self.m_FaceWithinScene = True
		self.m_FaceDetectionState = faceDetectionState
		self.m_TimeSpan_FaceTrackLoss = -1


	def update_mftrackerFace_Data(self, mftracker, ascDetectedFaceIndx, faceIsolated):
		window = mftracker.m_DetectedFace_WindowArray[ ascDetectedFaceIndx ]
		frame = mftracker.CurrFrame
		faceDetectionState = mftracker.m_DetectedFace_StateArray[ ascDetectedFaceIndx ]
		self.m_FaceDataReady = True
		self.m_Face_Window = window
		self.m_Face = frame[window[1]:window[1]+window[3], window[0]:window[0]+window[2]]
		self.m_FaceHSV = cv2.cvtColor(self.m_Face, cv2.COLOR_BGR2HSV)
		self.m_HSVHist = cv2.calcHist([self.m_FaceHSV], [0], None, [180], [0, 180])
		cv2.normalize(self.HSVHist, self.HSVHist, 0, 255, cv2.NORM_MINMAX)     # HSV Histogram
		self.m_FaceTracked = True
		self.m_ColMatchVal = 1.0
		self.m_FaceIsolated = faceIsolated
		self.m_FaceWithinScene = True
		self.m_FaceDetectionState = faceDetectionState
		self.m_TimeSpan_FaceTrackLoss = -1


# Structure for MultifaceTracker

class MFTracker:

	def __init__(self, frame=None, maxfacenum=0, colmatchthreshold=0, faceregionthreshold=0):

		# Current Frame
		self.CurrFrame = frame

		# Current frame's HSV transform
		if frame is not None:
			self.CurrHSVFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
		else:
			self.CurrHSVFrame = None
		
		# True when Detection/Reasoning data is ready
		self.ParameterDataReady = False

		# Number of faces seen so far
		self.GlobalNum = 0

		# Max. no. of faces allowed
		self.MaxFaceNum = maxfacenum

		# No. of current faces in active and passive state
		self.m_CurrFaceNum = 0

		# Array of MFTracker_Face objects for current faces
		self.m_FaceSet = [MFTracker_Face() for i in range(maxfacenum)]

		# No. of faces in active state
		self.m_ActiveFaceNum = 0

		# Array of FaceID's for active faces
		self.m_ActiveFaceIndxVec = np.zeros((self.MaxFaceNum), dtype=int)

		# No. of faces in passive state
		self.m_PassiveFaceNum = 0

		# Array of FaceID's for passive faces
		self.m_PassiveFaceIndxVec = np.zeros((self.MaxFaceNum), dtype=int)

		# No. of detected faces in current frame
		self.m_CurrDetectedFaceNum = 0

		# Array of window tuple for all the detected faces
		self.m_DetectedFace_WindowArray = []

		# Array of Face detection state
		self.m_DetectedFace_StateArray = np.zeros((self.MaxFaceNum), dtype=int)

		# Thresholds and Properties for use in Tracking
		self.m_ColMatchThreshold = colmatchthreshold

		# Detected and Tracked region overlap Threshold
		self.m_Tracked_Detected_FaceRegionOverlap_Threshold = faceregionthreshold

		# Matrix of Detected and Tracked Face region overlap value
		self.m_Tracked_Detected_FaceRegionOverlap_Matrix = np.zeros((self.MaxFaceNum, self.MaxFaceNum), dtype=float)

		# Maximum allowed time span for track loss
		self.m_MaxTimeSpan_FaceTrackLoss = 0

		# Array Storing the Number of Detected Face Regions Array Storing the Number of Detected Face Regions
		self.m_DetectedFaceNum_OverlappedWith_TrackedFaceRegion_Array = np.zeros((self.MaxFaceNum), dtype=int)

		# Array Storing the Number of Tracked Face Regions Overlapping with each Detected Face Region
		self.m_TrackedFaceNum_OverlappedWith_DetectedFaceRegion_Array = np.zeros((self.MaxFaceNum), dtype=int)

		# Array Storing the Number of Detected Faces Overlapping Each Other
		self.m_Detected_Face2Face_Overlap_Array = np.zeros((self.MaxFaceNum), dtype=int)

		# Array Storing the Number of Tracked Faces Overlapping Each Other
		self.m_Tracked_Face2Face_Overlap_Array = np.zeros((self.MaxFaceNum), dtype=int)

		# True if Reasoning Data is ready
		self.m_MFTrackerReasoningDataReady = False


	def __str__(self):
		return "MultifaceTracker with "+str(self.m_PassiveFaceNum)+" passive detected faces and "+str(self.m_ActiveFaceNum)+" active detected faces."


	def getActivePassiveFaceData(self):
		self.m_ActiveFaceNum = 0
		self.m_PassiveFaceNum = 0

		for i, face in enumerate(self.m_FaceSet):
			if face.m_FaceDataReady:
				if face.m_FaceTracked:
					self.m_ActiveFaceIndxVec[self.m_ActiveFaceNum] = i
					self.m_ActiveFaceNum += 1
				else:
					self.m_PassiveFaceIndxVec[self.m_PassiveFaceNum] = i
					self.m_PassiveFaceNum += 1
		self.m_CurrFaceNum = self.m_ActiveFaceNum + self.m_PassiveFaceNum


	def getAvailableFaceIndx(self):
		for counter in range( self.MaxFaceNum ):
			if not self.m_FaceSet[ counter ].m_FaceDataReady:
				return counter
		return -1


	def reset_mftracker_Reasoning_Data(self):
		self.m_Tracked_Face2Face_Overlap_Array = np.zeros((self.MaxFaceNum))
		self.m_Detected_Face2Face_Overlap_Array = np.zeros((self.MaxFaceNum))
		self.m_TrackedFaceNum_OverlappedWith_DetectedFaceRegion_Array = np.zeros((self.MaxFaceNum))
		self.m_DetectedFaceNum_OverlappedWith_TrackedFaceRegion_Array = np.zeros((self.MaxFaceNum))
		self.m_Tracked_Detected_FaceRegionOverlap_Matrix = np.zeros((self.MaxFaceNum, self.MaxFaceNum), dtype=float)
		self.m_MFTrackerReasoningDataReady = False


	def set_mftracker_Reasoning_Data(self):
		if self.m_CurrDetectedFaceNum > 0:

			if self.m_ActiveFaceNum > 0:

				for trackedFaceCount, faceIndx in enumerate( self.m_ActiveFaceIndxVec ):
					self.m_DetectedFaceNum_OverlappedWith_TrackedFaceRegion_Array[trackedFaceCount] = 0
					invFaceArea = 1.0 / ( self.m_FaceSet[ faceIndx ].m_Face_Window[2] * self.m_FaceSet[ faceIndx ].m_Face_Window[3] )
					for detectedFaceCount, window in enumerate( self.m_DetectedFace_WindowArray ):
						overlapVal = computeIntervalOverlap_2D( self.m_FaceSet[ faceIndx ].m_Face_Window, window )
						self.m_Tracked_Detected_FaceRegionOverlap_Matrix[ trackedFaceCount ][ detectedFaceCount ] = overlapVal
						fracOverlapVal1 = invFaceArea * overlapVal
						fracOverlapVal2 = overlapVal / ( window[2] * window[3] )
						if fracOverlapVal1 > self.m_Tracked_Detected_FaceRegionOverlap_Threshold or fracOverlapVal2 > self.m_Tracked_Detected_FaceRegionOverlap_Threshold:
							self.m_DetectedFaceNum_OverlappedWith_TrackedFaceRegion_Array[ trackedFaceCount ] += 1
				
				for detectedFaceCount, window in enumerate( self.m_DetectedFace_WindowArray ):
					self.m_TrackedFaceNum_OverlappedWith_DetectedFaceRegion_Array[ detectedFaceCount ] = 0
					invFaceArea = 1.0 / ( window[2] * window[3] )
					for trackedFaceCount, faceIndx in enumerate( self.m_ActiveFaceIndxVec ):
						fracOverlapVal1 = invFaceArea * self.m_Tracked_Detected_FaceRegionOverlap_Matrix[ trackedFaceCount ][ detectedFaceCount ]
						fracOverlapVal2 = self.m_Tracked_Detected_FaceRegionOverlap_Matrix[ trackedFaceCount ][ detectedFaceCount ] / ( self.m_FaceSet[ faceIndx ].m_Face_Window[2] * self.m_FaceSet[ faceIndx ].m_Face_Window[3] )

						if fracOverlapVal1 > self.m_Tracked_Detected_FaceRegionOverlap_Threshold or fracOverlapVal2 > self.m_Tracked_Detected_FaceRegionOverlap_Threshold:
							self.m_TrackedFaceNum_OverlappedWith_DetectedFaceRegion_Array[ trackedFaceCount ] += 1

				for detectedFaceCount, window in enumerate( self.m_DetectedFace_WindowArray ):

					invFaceArea = 1.0 / ( window[2] * window[3] )
					self.m_Detected_Face2Face_Overlap_Array[ detectedFaceCount ] = 0
					for counter, detected_window in enumerate( self.m_DetectedFace_WindowArray ):
						if counter != detectedFaceCount:
							overlapVal = computeIntervalOverlap_2D( window, detected_window )
							fracOverlapVal1 = overlapVal * invFaceArea
							fracOverlapVal2 = overlapVal / ( detected_window[2] * detected_window[3] )

							if fracOverlapVal1 > self.m_Tracked_Detected_FaceRegionOverlap_Threshold or fracOverlapVal2 > self.m_Tracked_Detected_FaceRegionOverlap_Threshold:
								self.m_Detected_Face2Face_Overlap_Array[ detectedFaceCount ] += 1

				for trackedFaceCount, faceIndx1 in enumerate( self.m_ActiveFaceIndxVec ):
					invFaceArea = 1.0 / ( self.m_FaceSet[ faceIndx1 ].m_Face_Window[2] * self.m_FaceSet[ faceIndx1 ].m_Face_Window[3] )
					self.m_Tracked_Face2Face_Overlap_Array[ trackedFaceCount ] = 0

					for counter, faceIndx2 in enumerate( self.m_ActiveFaceIndxVec ):
						overlapVal = computeIntervalOverlap_2D( self.m_FaceSet[ faceIndx1 ].m_Face_Window, self.m_FaceSet[ faceIndx2 ].m_Face_Window )
						fracOverlapVal1 = overlapVal * invFaceArea
						fracOverlapVal2 = overlapVal / ( self.m_FaceSet[ faceIndx2 ].m_Face_Window[2] * self.m_FaceSet[ faceIndx2 ].m_Face_Window[3] )
						if fracOverlapVal1 > self.m_Tracked_Detected_FaceRegionOverlap_Threshold or fracOverlapVal2 > self.m_Tracked_Detected_FaceRegionOverlap_Threshold:
							self.m_Tracked_Face2Face_Overlap_Array[ trackedFaceCount ] += 1

			else:
				for detectedFaceCount, window in enumerate( self.m_DetectedFace_WindowArray ):
					invFaceArea = 1.0 / ( window[2] * window[3] )
					self.m_Detected_Face2Face_Overlap_Array[ detectedFaceCount ] = 0

					for counter, detected_window in enumerate( self.m_DetectedFace_WindowArray ):
						if counter != detectedFaceCount:
							overlapVal = computeIntervalOverlap_2D( detected_window, window )
							fracOverlapVal1 = overlapVal * invFaceArea
							fracOverlapVal2 = overlapVal / ( detected_window[2] * detected_window[3] )

							if fracOverlapVal1 > self.m_Tracked_Detected_FaceRegionOverlap_Threshold or fracOverlapVal2 > self.m_Tracked_Detected_FaceRegionOverlap_Threshold:
								self.m_Detected_Face2Face_Overlap_Array[ detectedFaceCount ] += 1

		else:
			if self.m_ActiveFaceNum > 0:
				for trackedFaceCount, faceIndx1 in enumerate( self.m_ActiveFaceIndxVec ):
					invFaceArea = 1.0 / ( self.m_FaceSet[ faceIndx1 ].m_Face_Window[2] * self.m_FaceSet[ faceIndx1 ].m_Face_Window[3] )
					self.m_Tracked_Face2Face_Overlap_Array[ trackedFaceCount ] = 0

					for counter, faceIndx2 in enumerate( self.m_ActiveFaceIndxVec ):
						if counter != trackedFaceCount:
							overlapVal = computeIntervalOverlap_2D( self.m_FaceSet[ faceIndx1 ].m_Face_Window, self.m_FaceSet[ faceIndx2 ].m_Face_Window )
							fracOverlapVal1 = overlapVal * invFaceArea
							fracOverlapVal2 = overlapVal / ( self.m_FaceSet[ faceIndx2 ].m_Face_Window[2] * self.m_FaceSet[ faceIndx2 ].m_Face_Window[3] )
							if fracOverlapVal1 > self.m_Tracked_Detected_FaceRegionOverlap_Threshold or fracOverlapVal2 > self.m_Tracked_Detected_FaceRegionOverlap_Threshold:
								self.m_Tracked_Face2Face_Overlap_Array[ trackedFaceCount ] += 1

		self.m_MFTrackerReasoningDataReady = True


def computeIntervalOverlap_1D(s1, e1, s2, e2):
	if s1 <= s2:
		if e1 <= e2:
			return 0
		if ( s2 < e1 ) and ( e1 < e2 ):
			return e1 - s2
		if e1 > e2:
			return e2 - s2

	if ( s1 > s2 ) and ( s1 < e2 ):
		if e1 <= e2:
			return e1 - s1
		if e1 > e2:
			return e2 - s2
	if s1 > e2:
		return 0


def computeIntervalOverlap_2D( w1, w2 ):
	s1 = (w1[0], w1[1])
	e1 = (w1[0] + w1[2], w1[1] + w1[3])
	s2 = (w2[0], w2[1])
	e2 = (w2[0] + w2[2], w2[1] + w2[3])

	overlapX = computeIntervalOverlap_1D( s1[0], e1[0], s2[0], e2[0] )
	overlapY = computeIntervalOverlap_1D( s2[1], e2[1], s2[1], e2[1] )
	return overlapX * overlapY



def processActiveFace(mftracker, faceIndx, faceCount):
	
	invFaceArea = 1.0 / ( mftracker.m_FaceSet[ faceIndx ].m_Face_Window[2] * mftracker.m_FaceSet[ faceIndx ].m_Face_Window[3] )
	if mftracker.m_FaceSet[ faceIndx ].m_ColMatchVal > mftracker.m_ColMatchThreshold:
		if mftracker.m_DetectedFaceNum_OverlappedWith_TrackedFaceRegion_Array[ faceCount ] > 0:
			ascDetectedFaceIndx = -1
			maxOverlapVal = -1.0
			for detectedFaceCount in range( mftracker.m_CurrDetectedFaceNum ):
				overlapVal = mftracker.m_Tracked_Detected_FaceRegionOverlap_Matrix[ faceCount ][ detectedFaceCount ]
				if overlapVal > maxOverlapVal:
					maxOverlapVal = overlapVal
					ascDetectedFaceIndx = detectedFaceCount

			if ( mftracker.m_Detected_Face2Face_Overlap_Array[ ascDetectedFaceIndx ] == 0 ) and ( mftracker.m_TrackedFaceNum_OverlappedWith_DetectedFaceRegion_Array[ ascDetectedFaceIndx ] == 1):
				faceIsolated = True
				# need to be reviewed
				mftracker.m_FaceSet[ faceIndx ].update_mftrackerFace_Data(mftracker, ascDetectedFaceIndx, faceIsolated)

			else:
				mftracker.m_FaceSet[ faceIndx ].m_Face_Window = mftracker.m_DetectedFace_WindowArray[ ascDetectedFaceIndx ]
				mftracker.m_FaceSet[ faceIndx ].m_FaceTracked = True
				mftracker.m_FaceSet[ faceIndx ].m_FaceIsolated = False
				mftracker.m_FaceSet[ faceIndx ].m_FaceDetectionState = mftracker.m_DetectedFace_StateArray[ ascDetectedFaceIndx ]
				mftracker.m_FaceSet[ faceIndx ].m_TimeSpan_FaceTrackLoss = -1
		else:
			mftracker.m_FaceSet[ faceIndx ].m_FaceDetectionState = 0
			mftracker.m_FaceSet[ faceIndx ].m_FaceTracked = True
			mftracker.m_FaceSet[ faceIndx ].m_FaceIsolated = not ( mftracker.m_Tracked_Face2Face_Overlap_Array[ faceCount ] > 0 )
	else:
		if mftracker.m_DetectedFaceNum_OverlappedWith_TrackedFaceRegion_Array[ faceCount ] > 0:
			ascDetectedFaceIndx = -1
			maxOverlapVal = -1.0
			for detectedFaceCount in range( mftracker.m_CurrDetectedFaceNum ):
				overlapVal = mftracker.m_Tracked_Detected_FaceRegionOverlap_Matrix[ faceCount ][ detectedFaceCount ]
				if overlapVal > maxOverlapVal:
					maxOverlapVal = overlapVal
					ascDetectedFaceIndx = detectedFaceCount

			if ( mftracker.m_Detected_Face2Face_Overlap_Array[ ascDetectedFaceIndx ] == 0 ) and ( mftracker.m_TrackedFaceNum_OverlappedWith_DetectedFaceRegion_Array[ ascDetectedFaceIndx ] == 1 ):
				faceIsolated = True
				# needs to be reviewed
				mftracker.m_FaceSet[ faceIndx ].update_mftrackerFace_Data(mftracker, ascDetectedFaceIndx, faceIsolated)

			else:
				mftracker.m_FaceSet[ faceIndx ].m_Face_Window = mftracker.m_DetectedFace_WindowArray[ ascDetectedFaceIndx ]
				mftracker.m_FaceSet[ faceIndx ].m_FaceTracked = True
				mftracker.m_FaceSet[ faceIndx ].m_FaceIsolated = False
				mftracker.m_FaceSet[ faceIndx ].m_FaceDetectionState = mftracker.m_DetectedFace_StateArray[ ascDetectedFaceIndx ]
				mftracker.m_FaceSet[ faceIndx ].m_TimeSpan_FaceTrackLoss = -1
		else:
			mftracker.m_FaceSet[ faceIndx ].m_FaceTracked = False
			mftracker.m_FaceSet[ faceIndx ].m_TimeSpan_FaceTrackLoss = 0

	mftracker.m_FaceSet[ faceIndx ].m_FaceWithinScene = True


def processNewFaces(mftracker):

	for detectedFaceCount, detected_window in enumerate( mftracker.m_DetectedFace_WindowArray ):
		invFaceArea = 1.0 / ( detected_window[2] * detected_window[3] )
		
		if mftracker.m_TrackedFaceNum_OverlappedWith_DetectedFaceRegion_Array[ detectedFaceCount ] == 0:
			bestPassiveFaceIndx = -1
			bestOverlapVal = -1
			for faceCount, trackedFace in enumerate( mftracker.m_FaceSet ):
				tracked_window = trackedFace.m_Face_Window
				if mftracker.m_FaceSet[ faceCount ].m_FaceDataReady and (not mftracker.m_FaceSet[ faceCount ].m_FaceTracked ) :
					overlapVal = computeIntervalOverlap_2D(tracked_window, detected_window)
					if overlapVal > bestOverlapVal:
						bestPassiveFaceIndx = faceCount
						bestOverlapVal = overlapVal
			passiveFaceFound = False
			if bestPassiveFaceIndx >= 0:
				fracOverlapVal1 = bestOverlapVal *invFaceArea
				fracOverlapVal2 = bestOverlapVal / ( tracked_window[2] * tracked_window[3] )
				if fracOverlapVal1 > mftracker.m_Tracked_Detected_FaceRegionOverlap_Threshold or fracOverlapVal2 > mftracker.m_Tracked_Detected_FaceRegionOverlap_Threshold:
					passiveFaceFound = True

					if mftracker.m_Detected_Face2Face_Overlap_Array[ detectedFaceCount ] == 0:
						faceIsolated = True
						mftracker.m_FaceSet[ bestPassiveFaceIndx ].update_mftrackerFace_Data( mftracker, detectedFaceCount, faceIsolated )

					else:
						mftracker.m_FaceSet[ bestPassiveFaceIndx ].m_Face_Window = mftracker.m_DetectedFace_WindowArray[ detectedFaceCount ]
						mftracker.m_FaceSet[ bestPassiveFaceIndx ].m_FaceTracked = True
						mftracker.m_FaceSet[ bestPassiveFaceIndx ].m_FaceIsolated = False
						mftracker.m_FaceSet[ bestPassiveFaceIndx ].m_FaceDetectionState = mftracker.m_DetectedFace_StateArray[ detectedFaceCount ]
						mftracker.m_FaceSet[ bestPassiveFaceIndx ].m_TimeSpan_FaceTrackLoss = -1

			if not passiveFaceFound:
				faceID = -1
				faceID = mftracker.getAvailableFaceIndx()
				if (faceID >= 0) and ( faceID < mftracker.MaxFaceNum ):
					mftracker.GlobalNum += 1
					mftracker.m_FaceSet[ faceID ].set_mftrackerFace_Data( mftracker, detectedFaceCount, faceID )
					print("Set the data for new Face.")
				else:
					print(" Face ARRAY OVERFLOW ")


def multifacetracker(mftracker):
	term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )

	mftracker.getActivePassiveFaceData()

	if mftracker.m_ActiveFaceNum > 0:
		for faceCount, faceIndx in enumerate( mftracker.m_ActiveFaceIndxVec ):
			print(" Face Index --> "+str(faceIndx))
			print(type(mftracker.CurrHSVFrame), type(mftracker.m_FaceSet[ faceIndx ].m_HSVHist))
			dst = cv2.calcBackProject([ mftracker.CurrHSVFrame ], [0], mftracker.m_FaceSet[ faceIndx ].m_HSVHist , [0,180], 1,)
			ret, mftracker.m_FaceSet[ faceIndx ].m_Face_Window = cv2.CamShift(dst, mftracker.m_FaceSet[ faceIndx ].m_Face_Window, term_crit)
		
		mftracker.reset_mftracker_Reasoning_Data()
		mftracker.set_mftracker_Reasoning_Data()

		for faceCount, faceIndx in enumerate( mftracker.m_ActiveFaceIndxVec ):
			processActiveFace( mftracker, faceIndx, faceCount )
		
		if mftracker.m_CurrDetectedFaceNum > 0:
			processNewFaces( mftracker )

			for faceCount in range( mftracker.MaxFaceNum ):
				if mftracker.m_FaceSet[ faceCount ].m_FaceDataReady:
					if (not mftracker.m_FaceSet[ faceCount ].m_FaceTracked ) or ( not mftracker.m_FaceSet[ faceCount ].m_FaceWithinScene ) :
						mftracker.m_FaceSet[ faceCount ].m_TimeSpan_FaceTrackLoss += 1
					
					if mftracker.m_FaceSet[ faceCount ].m_TimeSpan_FaceTrackLoss > mftracker.m_MaxTimeSpan_FaceTrackLoss:
						mftracker.m_FaceSet[ faceCount ].reset_mftrackerFace_Data()

		else:
			for faceCount in range( mftracker.MaxFaceNum ):
				if mftracker.m_FaceSet[ faceCount ].m_FaceDataReady:
					if ( not mftracker.m_FaceSet[ faceCount ].m_FaceTracked ) or ( mftracker.m_FaceSet[ faceCount ].m_FaceWithinScene ):
						mftracker.m_FaceSet[ faceCount ].m_TimeSpan_FaceTrackLoss += 1
					if mftracker.m_FaceSet[ faceCount ].m_TimeSpan_FaceTrackLoss > mftracker.m_MaxTimeSpan_FaceTrackLoss:
						mftracker.m_FaceSet[ faceCount ].reset_mftrackerFace_Data()
	else:
		mftracker.reset_mftracker_Reasoning_Data()
		mftracker.set_mftracker_Reasoning_Data()

		if mftracker.m_CurrDetectedFaceNum > 0:
			processNewFaces(mftracker)
			print("Processed a new Face..")
		else:
			print(" ActiveFaceNum = 0 AND DetectedFaceNum = 0")

def processActiveFace():
	return True

'''
functions need to be implemented
1. getAvailableFaceIndx() - --------------------> Done
2. computeIntervalOverlap_2D()  ----------------> Done
3. processActiveFace()  ------------------------> Done
'''
