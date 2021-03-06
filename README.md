# dexa_analysis
Analyze DEXA dicom images

This is a tool for the analysis of bone density scans of the spine (DEXA). The application uses computer vision (OpenCV) to measure the scoliosis angle of the spine and to assess the proper position of the spine in the region of interest (ROI). It is available with a Tkinter GUI. The development is part of my Master's theses. 

Computer vision for the evaluation of  DXA scans of the lumbar spine

Introduction:
Dual-energy X-ray absorptiometry (DXA) is  x-ray method for the assessment of the bone mineral density (BMD) and is considered the “gold standard” world-wide. DXA is  performed on the 4 lumbar vertebrae (L1-L4) and BMD is measured for each of them as well as total. From the BMD value the software calculates a T-score value as a standard deviation (SD) from the BMD of a healthy 30-year old individual. There are several guidelines how to perform the assessment and a few issues that could compromise the reliability of the results: lumbar scoliosis and improper ROI position. Lumbar scoliosis is a curve in the lumbar spine. The ROI should be placed such that the spine is centered and the amount of soft tissue on both sides is equal. The resulting discrepancy is a difference between the T-scores of the vertebrae (>1.0 SD).

Objective:
The objective of this work is to use computer vision to create a computer model for evaluation of the results from a DXA analysis. This evaluation includes the calculation of the angle of the scoliosis curve and inspection of the region of interest (ROI) for proper position. The model is used to create a computer application and for statistical analysis to interpret how these conditions affect the results.

Methods:
For the creation of the computer model we use OpenCV library for Python and the main methods for feature detection and feature extraction. To calculate the angle of scoliosis we use Canny’s edge detector and Hough transform. To inspect the ROI we use contours to calculate the deviation of the spine from the center of the ROI. The format of the DXA reports is DICOM and we use PyDICOM to process the files. For statistical analysis we use Chi-square test on the results from the evaluation of 600 DXA reports with the model.

Results:
The model calculates the angle of the scoliosis curve accurately supported by a comparison with a human measurement with a DICOM image software. The application calculates the deviation of the spine from the center of the ROI in pixels (px). The results from the evaluation with the model of 600 DXA reports showed that 73 people had scoliosis with angle > 5 °. These 73 subjects were divided into four groups: the first group with deviation of the spine < 10 px and T-score difference < 1.0 SD; the second group with deviation < 10 px and T-score difference > 1.0 SD; the third group with deviation > 10 px and T-score difference <1.0 SD; the last with deviation >10 px and T-score difference > 1.0 SD. Chi-square test showed a statistically significant difference between the groups with p=0.03 caused by the deviation of the spine from the center of the ROI.

Conclusion:
The created computer model calculates effectively the lumbar scoliosis angle and can successfully be used for screening of patients from DXA reports. Scoliosis with an angle greater than 5 ° may create discrepancies in the results and in the interpretation of the whole assessment.
