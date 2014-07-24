import pystanLoad as pyL

casheDirectory = './cache'

# Below is an example of running the analysis on experimental data.

runType = "MC"

if runType=="Data":
    theModel = './krypton_analysis.stan'
    theDataFiles = {'header':'./data/krypton_run.header.data', 'data':'./data/krypton_run.data'}
    theSample= "./results/test_analysis.out"
    thePlots = ['TotalField','TrappingField','MainField','frequency','SourceMean','SourceWidth','KE','stheta','dfdt']
else :
    theModel = './krypton_generator.stan'
    theDataFiles = {'header':'./data/krypton_run.header.data', 'mc':'./data/krypton_monte_carlo.data'}
    theSample= "./results/test_generator.out"
    thePlots = ['TotalField','TrappingField','MainField','KE','frequency','freq_data','dfdt']

# Run fitter

theData = pyL.stan_data_files(theDataFiles)

fit = pyL.stan_cache(model_code= theModel, 
		 cashe_dir= casheDirectory,
		 data=theData,
		 iter=2500, chains=8,
		 sample_file=theSample)

# Print results and make plots

print(fit)

for key in thePlots:
    fit.plot(key)

pyL.plt.show()
