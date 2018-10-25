from morpho.processors.sampling import PyStanSamplingProcessor
import math

fitter_config = {
        "model_code": "integral/models/model_integral.stan",
        "input_data": {
            "threshold": 10000,
            "count": 1000
            },
        "include_dirs": ["integral/models"],
        "includes": ["integral.hpp"],
        "allow_undefined": True,
        "iter": 22000,
        "warmup": 2000,
        "interestParams": ['amplitude'],
}

fitterProcessor = PyStanSamplingProcessor("fitter")
fitterProcessor.Configure(fitter_config)
fitterProcessor.Run()

threshold = fitter_config["input_data"]["threshold"]
count = fitter_config["input_data"]["count"]

from ROOT import TFile, TH1D
f = TFile("integral/models/model_input/spectrum.root", "READ")
hist = (TH1D)(f.Get("th"))
hist.Scale(1./hist.Integral())

low = hist.FindBin(threshold)
up = hist.GetNbinsX()
integral = hist.Integral(low, up)

error = math.sqrt(count)/count
print("Expected fitting result for amplitude: ", count/integral, " \pm ", count/integral * error)

