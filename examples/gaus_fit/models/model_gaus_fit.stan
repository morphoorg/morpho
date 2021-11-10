functions{
	
	real normal_density(real x, real theta[], real x_r[], int x_i[]) {

		real mu = theta[1];
		real sigma = theta[2];

		return 1 / (sqrt(2*pi()) * sigma) * exp(-0.5*((x-mu)/sigma)^2);
	}
}

data{

	int N;
	real y[N];

}

transformed data{
	real x_r[0];
	int x_i[0];

}

parameters{
	
	real mu;
	real<lower=0.0> sigma;
	real<lower=0.0> sigma_y_smear;

}

transformed parameters{}

model{

	mu ~ normal(0,1);
	sigma ~ normal(0,1);
	target += normal_lpdf(y | mu, sigma);

}

generated quantities{

	real variance_y;
	variance_y = sigma * sigma;
}

