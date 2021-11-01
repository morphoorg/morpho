data {
	real mu1;
	real sigma1;
	real sigma1_y_smear;
	real mu2;
	real sigma2;
	real sigma2_y_smear;
}

parameters {

	real x;
	real y;

}

model {

	target += normal_lpdf(y - (1 / (sqrt(2*pi()*(square(sigma1) + square(sigma2)))) * exp(square((x-(mu1+mu2)))/(2*(square(sigma1) + square(sigma2))))) | 0, sigma1_y_smear); // square root of s1^2+s2^2?
}

generated quantities {
	real residual;
	residual = (y - (1 / (sqrt(2*pi()*(square(sigma1) + square(sigma2))))) * exp(-(square((x-(mu1+mu2)))/(2*(square(sigma1) + square(sigma2)))))/sigma1_y_smear; 
}


