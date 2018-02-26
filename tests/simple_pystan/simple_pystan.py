from morpho.processors.sampling import PyStanSamplingProcessor

pystan_config = {
    "model_code": "model.stan",
    "input_data": "",
    "iterations": 100
}

pystanProcessor = PyStanSamplingProcessor("pystanProcessor")
pystanProcessor.Configure(pystan_config)
print(pystanProcessor.Run())

