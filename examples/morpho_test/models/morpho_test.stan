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

		real<lower=7, upper=13> theta2;
		real<lower=-3, upper=3> theta;

}


model{

	theta ~ normal(0,1);
  theta2 ~ normal(10,1);

}
