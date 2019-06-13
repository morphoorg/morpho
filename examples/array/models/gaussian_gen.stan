data {
    int dim__means;
    vector[dim__means] means;
    real<lower=0> widths[dim__means];
}

parameters {
    vector[dim__means] x;
}

model {
    target +=normal_lpdf(x-means|0,widths);
}

generated quantities {
}