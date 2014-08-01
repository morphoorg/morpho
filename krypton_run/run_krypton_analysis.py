import json
import sys
import pystanLoad as pyL

theConfigFile = sys.argv[1]
print "Using configuration file :",theConfigFile

# Load in configuration file

json_file = open(theConfigFile).read()
json_data = json.loads(json_file)
config_file = pyL.readLabel(json_data,'stan','./run.json')

# Set up the stan model and cache directory

theModel = pyL.readLabel(config_file, 'model')
casheDirectory = pyL.readLabel(theModel, 'cache', './cache')
theModelFile =  pyL.readLabel(theModel,'file')
     
# Set up the input, output and plotting configurations
theDataFiles =  pyL.readLabel(config_file, 'data')
theSample = pyL.readLabel(config_file,'sample')
thePlots =  pyL.readLabel(config_file,'plot')


# Set up running conditions
theRunConditions =  pyL.readLabel(config_file,'run')
theAlgorithm =  pyL.readLabel(theRunConditions,'algorithim','NUTS')
nIter =   pyL.readLabel(theRunConditions,'iter',2000)
nChain =  pyL.readLabel(theRunConditions,'chain',4)

# Load in the data
theData = pyL.stan_data_files(theDataFiles)

# Execute the fit
theFit = pyL.stan_cache(model_code= theModelFile, 
		 cashe_dir= casheDirectory,
		 data=theData,
		 algorithm = theAlgorithm, 
		 iter=nIter, chains=nChain,
		 sample_file=theSample)

# Print results and make plots

print(theFit)

for key in thePlots:
    theFit.plot(key['variable'])

pyL.plt.show()
