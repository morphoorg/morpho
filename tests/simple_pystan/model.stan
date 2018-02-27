parameters {
    real x;
    real y;
}

model {
    target +=normal_lpdf(x|0,1);
    target +=normal_lpdf(y|0,1);
}