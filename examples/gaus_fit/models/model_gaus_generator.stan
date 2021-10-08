data {
	real mu;
	real sigma;
}

parameters {
	real x;
	real y;
}

model {
	target +=normal_lpdf(y-mu|0,sigma);
}

generated quantities {
	real residual;
	residual = (y - mu)/sigma;
}