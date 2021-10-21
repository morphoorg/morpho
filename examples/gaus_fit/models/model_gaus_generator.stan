data {
	real mu;
	real sigma;
	real sigma_y_smear;
}

parameters {

	real x;
	real y;

}

model {

	target += normal_lpdf(y - (1 / sigma*sqrt(2*pi()) * exp(-0.5*(((x - mu)/sigma)^2))) | 0, sigma_y_smear);
}

generated quantities {
	real residual;
	residual = (y - (1 / sigma*sqrt(2*pi()) * exp(-0.5*(((x - mu)/sigma)^2))))/sigma_y_smear; 
}


