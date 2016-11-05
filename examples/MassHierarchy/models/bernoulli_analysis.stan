/*
* MC Neutrino Mass and Beta Decay Model - Bernoulli post-analysis
* -------------------------------------------------------------------
* Author: Talia Weiss <tweiss@mit.edu>
*
* Date: 27 August 2016
*
* Purpose:
*
* Constructs a Bernoulli parameter: a measure of the extent to which
* the data is consistent with the normal hierarchy.
*
*/



data{

	int len_m32;
	vector[len_m32] m32_withsign;

}



transformed data{

	int is_NH[len_m32];

	for (i in 1:len_m32){
	    is_NH[i] = ((m32_withsign[i] > 0)? 1 : 0);
	     }

}



parameters{

	real<lower=0.0, upper=1.0> theta;

}


model{

        is_NH ~ bernoulli(theta);

}