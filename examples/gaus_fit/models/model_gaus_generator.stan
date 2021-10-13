data {
	real mu;
	real sigma;
}

parameters {
	real x;
	real y;
}

model {

	target += normal_lpdf(y | mu, sigma);
}

generated quantities {
	real residual;
	residual = (y - 1 / ( sigma * sqrt ( 2 * pi() ) ) * e()^(-0.5* (x - mu)/sigma) )/sigma; //change this line too
}


