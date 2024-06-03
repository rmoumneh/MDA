[![Tests](https://github.com/Tryfonm/python-template/actions/workflows/tests.yml/badge.svg)](https://github.com/Tryfonm/python-template/actions/workflows/tests.yml)

The main entrypoint of the application is src/scripts/run_simulation.py.
Keep in mind that the application given the full dataset DOES NOT run in feasible times. For this reason two arguments are used to undersample the initial dataset. By default they reduce the dataset size to around 20% of its original. By running the script a folder /runs will be created saving the graphs of each iteration and the logger can be easily to as well write details on disk (currently is configured to send to standard output only).

## Usage
python src/scripts/run_simulation.py --iterations <iterations> [--samples_per_iteration <samples_per_iteration>] [--eps <eps>] [--min_samples <min_samples>] [--aed_undersample <aed_undersample>] [--interventions_undersample <interventions_undersample>]

- iterations (required): Number of iterations to run the simulation; equivalent to the number of AEDs to add.
- samples_per_iteration (optional): Defines the sampling count for each iteration. Default is 1000.
- eps (optional): DBSCAN epsilon parameter. Default is 0.0001.
- min_samples (optional): DBSCAN min_samples parameter for forming clusters. Default is 5.
- aed_undersample (optional): Undersample parameter for the aed_df to avoid the app from crashing. Default is 1000.
- interventions_undersample (optional): Undersample parameter for the interventions_df to avoid the app from crashing. Default is 4000.

python src/scripts/run_simulation.py --iterations 10 --samples_per_iteration 1500 --eps 0.001 --min_samples 10 --aed_undersample 500 --interventions_undersample 2000

Please ignore the notebooks/ folder; it's been used for prototyping only.