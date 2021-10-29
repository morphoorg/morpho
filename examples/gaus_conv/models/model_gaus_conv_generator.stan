data {
	real mu1;
	real sigma1;
	real sigma_y1_smear;
	real mu2;
	real sigma2;
	real sigma_y2_smear;
}

parameters {

	real x1;
	real y1;
	real x2;
	real y2;

}

model {

	target += normal_lpdf(y - (1 / sigma*sqrt(2*pi()) * exp(-0.5*(((x - mu)/sigma)^2))) | 0, sigma_y_smear);
}

generated quantities {
	real residual;
	residual = (y - (1 / sigma*sqrt(2*pi()) * exp(-0.5*(((x - mu)/sigma)^2))))/sigma_y_smear; 
}


