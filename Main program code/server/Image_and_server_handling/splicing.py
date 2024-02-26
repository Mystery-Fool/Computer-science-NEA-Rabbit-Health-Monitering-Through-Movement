import cv2
import numpy as np
from matplotlib import pyplot as plt
from stitching.images import Images
from stitching.feature_detector import FeatureDetector
from stitching.feature_matcher import FeatureMatcher
from stitching.subsetter import Subsetter
from stitching.camera_estimator import CameraEstimator
from stitching.camera_adjuster import CameraAdjuster
from stitching.camera_wave_corrector import WaveCorrector
from stitching.warper import Warper
from stitching.cropper import Cropper
from stitching.seam_finder import SeamFinder
from stitching.exposure_error_compensator import ExposureErrorCompensator
from stitching.blender import Blender
#made using https://github.com/OpenStitching/stitching_tutorial/blob/master/docs/Stitching%20Tutorial.md
#image cropping from https://pyimagesearch.com/2018/12/17/image-stitching-with-opencv-and-python/



class stitch():
	"""
	Class for image stitching using OpenCV and Python. Some features have been restricted to speed up results.

	Args:
		None

	Attributes:
		first_run (bool): Flag to indicate if it's the first run of the stitching process, used to speed up stitching first run ~ 6 seconds following ~1.5.
		images (Images): Object to handle loading and resizing of images.
		low_imgs (list): List of low-resolution images.
		medium_imgs (list): List of medium-resolution images.
		final_imgs (list): List of final-resolution images.
		features (list): List of detected features in the images.
		matches (list): List of matched features between images.
		cameras (list): List of estimated camera parameters.

	Methods:
		Private:
		__Prep_imgs(image1path, image2path): Prepare the images for stitching.
		__Find_and_match(): Find and matches the features in the images only run once.
		__Subset(): Subsets the images and features.
		__Camera_function(): Estimate camera parameters and adjust them only run once.
		__Putting_together(): Perform image warping, seam finding, exposure error compensation, and blending.
		__Save_img(name): Save the stitched panorama image.

		Public:
		stitch_and_save(image1path, image2path, name): Stitch two images together and save the resulting panorama.
	"""

	def __init__(self):
		self.first_run = True
		self.images = []
		self.low_imgs = []
		self.medium_imgs = []
		self.final_imgs = []
		self.features = []
		self.matches = []
		self.cameras = []

		while True: #Repeat over till confidence score is high enough to match images
			try: 
				self.stitch_and_save("Image_and_server_handling\\Prep_images\\test13L.png", "Image_and_server_handling\\Prep_images\\test13R.png", "Image_and_server_handling\\Prep_images\\test13.png")
			except:
				pass
			else:
				self.first_run = False
				break

	def stitch_and_save(self, image1path, image2path, name):
		"""
		Stitch two images together and save the resulting combined image.

		Args:
			image1path (str): Path to the first image.
			image2path (str): Path to the second image.
			name (str): Name of the output panorama image.
		"""
		self.__Prep_imgs(image1path, image2path)
		if self.first_run:
			self.__Find_and_match()

		self.__Subset()
		if self.first_run:
			self.__Camera_function()

		self.__Putting_together()
		self.__Save_img(name)

	def __Prep_imgs(self, image1path, image2path):
		"""
		Prepare the images for stitching by loading the images and resizing them to different resolutions.

		Args:
			image1path (str): Path to the first image.
			image2path (str): Path to the second image.
		"""
		load_images = [image1path, image2path]
		self.images = Images.of(load_images)
		self.low_imgs = list(self.images.resize(Images.Resolution.LOW))
		self.medium_imgs = list(self.images.resize(Images.Resolution.MEDIUM))
		self.final_imgs = list(self.images.resize(Images.Resolution.FINAL))

	def __Find_and_match(self):
		"""
		Finds and matches the features in the images.
		This uses the ORB detector to find features and matches them using a feature matcher. It is only run once per execution.
		"""
		finder = FeatureDetector(detector='orb', nfeatures=5000000) #sift also returns a valid value
		matcher = FeatureMatcher()#Altenative matcher_type='affine'
		self.features = [finder.detect_features(img) for img in self.medium_imgs]
		self.matches = matcher.match_features(self.features)

	def __Subset(self):
		"""
		Subsets the images and features.
		This method subsets the features based to create a confidence matrix.
		"""
		if self.first_run==True:
			self.subsetter = Subsetter(confidence_threshold=1.0)
			self.indices = self.subsetter.get_indices_to_keep(self.features, self.matches)

		self.medium_imgs = self.subsetter.subset_list(self.medium_imgs, self.indices)
		self.low_imgs = self.subsetter.subset_list(self.low_imgs, self.indices)
		self.final_imgs = self.subsetter.subset_list(self.final_imgs, self.indices)
		self.features = self.subsetter.subset_list(self.features, self.indices)
		self.matches = self.subsetter.subset_matches(self.matches, self.indices)
		self.images.subset(self.indices)

	def __Camera_function(self):
		"""Estimate camera parameters and adjust them.

		This method estimates the camera parameters using the detected features and matches.
		It also adjusts the camera parameters and performs wave correction.
		It is only run once per execution.

		"""
		camera_estimator = CameraEstimator()
		camera_adjuster = CameraAdjuster()
		wave_corrector = WaveCorrector()
		self.cameras = camera_estimator.estimate(self.features, self.matches)
		self.cameras = camera_adjuster.adjust(self.features, self.matches, self.cameras)
		self.cameras = wave_corrector.correct(self.cameras)

	def __Putting_together(self):
		"""Perform image warping, seam finding, exposure error compensation, and blending.

		This method warps the images, finds seams for blending, compensates for exposure errors,
		and blends the two images together to create the final panorama.

		"""
		if self.first_run:
			self.warper = Warper()
			self.warper.set_scale(self.cameras)
			low_sizes = self.images.get_scaled_img_sizes(Images.Resolution.LOW)
			camera_aspect = self.images.get_ratio(Images.Resolution.MEDIUM, Images.Resolution.LOW)
			warped_low_imgs = list(self.warper.warp_images(self.low_imgs, self.cameras, camera_aspect))
			warped_low_masks = list(self.warper.create_and_warp_masks(low_sizes, self.cameras, camera_aspect))
			low_corners, low_sizes = self.warper.warp_rois(low_sizes, self.cameras, camera_aspect)
			self.camera_aspect = self.images.get_ratio(Images.Resolution.MEDIUM, Images.Resolution.FINAL)

		final_sizes = self.images.get_scaled_img_sizes(Images.Resolution.FINAL)
		warped_final_imgs = list(self.warper.warp_images(self.final_imgs, self.cameras, self.camera_aspect))
		warped_final_masks = list(self.warper.create_and_warp_masks(final_sizes, self.cameras, self.camera_aspect))
		final_corners, final_sizes = self.warper.warp_rois(final_sizes, self.cameras, self.camera_aspect)

		if self.first_run:
			self.seam_finder = SeamFinder()
			seam_masks = self.seam_finder.find(warped_low_imgs, low_corners, warped_low_masks)
			self.seam_masks = [self.seam_finder.resize(seam_mask, mask) for seam_mask, mask in zip(seam_masks, warped_final_masks)]
			self.compensator = ExposureErrorCompensator()
			self.compensator.feed(low_corners, warped_low_imgs, warped_low_masks)

		compensated_imgs = [self.compensator.apply(idx, corner, img, mask) for idx, (img, mask, corner) in enumerate(zip(warped_final_imgs, warped_final_masks, final_corners))]

		if self.first_run:
			self.blender = Blender(blender_type='no', blend_strength=5)

		self.blender.prepare(final_corners, final_sizes)
		for img, mask, corner in zip(compensated_imgs, self.seam_masks, final_corners):
			self.blender.feed(img, mask, corner)

		self.panorama, _ = self.blender.blend()

	def __Save_img(self, name):
		"""Save the stitched images.

		Args:
			name (str): Name of the output image.

		"""
		cv2.imwrite(name, self.panorama)
