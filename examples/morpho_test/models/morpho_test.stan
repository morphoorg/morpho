/*
* MC morpho testing model
* -------------------------------------------------------------------
* Author: Mathieu Guigue <mathieu.guigue@pnnl.gov>
*
* Date: December 5th 2016
*
* Purpose:
*
* Generic and simple model for testing
*
*/



data{

}



transformed data{



}



parameters{

	real<lower=-10, upper=10> theta;

}


model{

        theta ~ normal(0,1);

}
