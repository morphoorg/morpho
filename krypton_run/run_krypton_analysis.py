import json
import sys
import pystanLoad as pyL

theConfigFile = sys.argv[1]
print "Using configuration file :",theConfigFile

json_file = open(theConfigFile).read()

json_data = json.loads(json_file)
config_file = json_data['stan']

casheDirectory = config_file['model']['cache']

theModel = config_file['model']['file']
     
theDataFiles = config_file['data']

theSample = config_file['sample']
     
thePlots = config_file['plot']

theAlgorithm =  config_file['run']['algorithim']
nIter =  config_file['run']['iter']
nChain = config_file['run']['chain']

theData = pyL.stan_data_files(theDataFiles)

theFit = pyL.stan_cache(model_code= theModel, 
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
