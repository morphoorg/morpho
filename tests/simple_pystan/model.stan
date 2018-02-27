parameters {
    real x;
}

model {
    target +=normal_lpdf(x|0,1);
}