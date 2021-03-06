# ENCODE_imputation_challenge

This code is necessary to reproduce the BrokenNodes_v3 predictions of the Encode Imputation challenge.
If you are willing to reproduce BrokenNodes_v2 imputation, it is sufficient to change the input tracks to just signals coming from training (T) and validation (V).
To reproduce the BrokenNodes imputation it is necessary to change the input (always just training (T) and validation (V) tracks) and transform directly the assay based predictions with the sinh function.

## Training code
We used it to pre-process the necessary input tracks starting from the .bigWig files, down-sampling the tracks at 25 bp resolution and transforming them with the sinh^-1 function.
During the training part, since the model is based on KNN, we compute the correlation between different cells and different assays as explained in section \ref{sec:data} (it is important to specify that the correlation is computed starting from the down-sampled .numpy tracks that are not transformed with the sinh^-1 function).
* **Pre-processing.py inputPATH outputPATH sinhPATH**: takes the inputPATH of the folder were the .bigWig tracks are stored, the outputPATH were to store the .numpy down-sampled at 25 bp tracks, and the sinhPATH were to store the .numpy down-sampled at 25 bp tracks transformed with sinh^-1.
* **Pearson.py inputPATH**: takes the inputPATH of all the 25 bp .numpy training (T) tracks in order to save in the respective folder a 267X267 similarity matrix (this corresponds to the correlation between all the tracks of (T)). Important: even if we are using as input tracks the folder that contains (T), (V), and imputed (B) signals, the script will use signals just coming from the training (T) set.
* **C_cA_a.py**: extracts from the previously computed similarity matrix 267X267 two matrices outAxA.csv, outCxC.csv, respectively 35X35 and 51X51 (they represent a similarity measure between all the assays of the dataset and all the cells of the dataset).
* **Workflow**: (1.) First make sure to have all the necessary .bigWig tracks in a folder. (2.) Run the Pre-processing.py making sure to have in the same folder the GRCh38\_chrom\_sizes.txt. (3.) Run the Pearson.py making sure to have the signals file in the same folder and insert as inputPATH the path of the pre-processed signals NOT transformed with the sinh^-1. The script will save in its folder the similarity.npy matrix. (4.) Run the C_cA_a.py script making sure to have the similarity.npy in the same folder. The script will output two matrices outAxA.csv and outCxC.csv.

## Prediction code
We have the assay-based and cell-based prediction and the aggregated prediction that will deliver the final imputed tracks. The assay-based and cell-based prediction scripts require as input tracks the sinh^-1 transformed signals computed with the Pre-processing.py code.

* **AssayPrediction.py inputPATH outputPATH**: requires as inputPATH the path to the folder were are stored the input tracks transformed with sinh^-1 transformation, the input for the BrokenNodes_v3 prediction will require the training tracks (T), the validation tracks (V) and the Avocado imputed tracks (B)). The ouputPATH will define the folder were the predictions are scored.
    
* **CellPrediction.py inputPATH outputPATH**: has the same requirements as the AssayPrediction.py, but performs the cell-based prediction instead of the assay-based prediction.
    
* **MergeAssayCells.py assayPATH cellPATH outputPATH**: takes the assayPATH where the predictions coming from AssayPrediction.py are stored, and cellPATH where the predictions coming from the CellPrediction.py are stored. In the outputPATH the final predictions of the blind tracks (B) will be saved, ready to be scored (they are transformed back to the original scale with the $\sinh$ function).
    
* **Workflow**: (1.) Make sure to have in the same folder the following files: validation\_labels, signals, outCxC.csv, outAxA.csv, MetadataTable.csv. (2.) Run the AssayPrediction.py (3.) Run the CellPrediction.py. (4.) Run the MergeAssayCells.py making sure to insert as input paths the ones related to the predictions generated in the two previous steps. This final script will provide the final predictions for the BrokenNodes_v3 submission on the blind (B) set.
