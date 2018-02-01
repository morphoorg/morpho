library("bayesplot")

if (div_plot %in%) {
mcmc_scatter(
	posterior_cp,
	pars = c("theta[1]", "tau"),
	#transform = list(tau = "log"), # actually show log(tau)
        np = np_cp
	)