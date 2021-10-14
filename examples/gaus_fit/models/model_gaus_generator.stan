data {
	real mu;
	real sigma;
}

parameters {

	real x;
	real y;
}

model {

	target += normal_lpdf(y - 1 / sigma*sqrt(2*pi()) * exp(-0.5*((x-mu)^2/(sigma^2)))) | mu, sigma);
}

generated quantities {
	real residual;
	residual = (y - 1 / sigma*sqrt(2*pi()) * exp(-0.5*((x-mu)^2/(sigma^2))))/sigma; 
}


