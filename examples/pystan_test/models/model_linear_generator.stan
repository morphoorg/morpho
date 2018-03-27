data {
    real intercept;
    real slope;
    real sigma;
    real xmin;
    real xmax;
}

parameters {
    real<lower=xmin, upper=xmax> x;
    real y;
}

model {
    target +=normal_lpdf(y-slope*x-intercept|0,sigma);
}

generated quantities {
    real residual;
    residual = (y - slope*x-intercept)/sigma;
}