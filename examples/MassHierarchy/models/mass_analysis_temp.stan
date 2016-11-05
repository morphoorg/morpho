/*
* MC Neutrino Mass and Beta Decay Model - Mass Analyzer (no spectrum)
* -------------------------------------------------------------------
* Author: Talia Weiss <tweiss@mit.edu>
*
* Date: 10 August 2016
*
* Purpose:
*
* Constructs neutrino mass model in Stan given an input distribution
* for either m_beta or m_s=m1+m2+m3.
*
* This ("temporary") model does not yet incorporate asymmetric
* errors on mixing parameters (the asymmetric gaussian function
* currently has trouble with particular parameters).
*
*/





functions{

	// Load libraries

	include=constants;
    	include=func_routines;
    	include=neutrino_mass_functions;

}


data{

	int nExp_th12;			// Number of experiments from which neutrino
	int nExp_th13;    		// parameter distributions are inputted
	int nHierarchyDep_th13;

	int nExp_m21;
	int nExp_m32_NH;
	int nExp_m32_IH;
	int nExp_m13_IH;	

	real sin2_th12_means[nExp_th12];	// Means from each experiment
	vector[nExp_th12] sin2_th12_sigmas; // Standard devs from each

			  			  // see func_routines.functions

	real sin2_th13_means[nExp_th13];
	vector[nExp_th13] sin2_th13_sigmas;

	real sin2_th13_means_NH[nHierarchyDep_th13];
	real sin2_th13_means_IH[nHierarchyDep_th13];
	vector[nHierarchyDep_th13] sin2_th13_sigmas_NH;
	vector[nHierarchyDep_th13] sin2_th13_sigmas_IH;


	real delta_m21_means[nExp_m21];
	vector[nExp_m21] delta_m21_sigmas;

	real delta_m32_means_NH[nExp_m32_NH];
	real delta_m32_means_IH[nExp_m32_IH];
	vector[nExp_m32_NH] delta_m32_sigmas_NH;
	vector[nExp_m32_IH] delta_m32_sigmas_IH;

	real delta_m13_means_IH[nExp_m13_IH];
	real delta_m13_sigmas_IH[nExp_m13_IH];

	real m_beta_squared_mean;	// m_beta_squared = sum(U_{e,i}^2*m_i^2)
	real m_beta_squared_sigma;

	real m_s_mean;			// m_s = sum(m_i)
	real m_s_sigma;

	int use_m_beta;			// 0 -> False, 1 -> True
	int use_m_s;
}


parameters{

	vector<lower=0.0, upper=0.4>[3] nu_mass;

	real<lower=0.0, upper=0.5> sin2_th12;
	real<lower=0.0, upper=0.1> sin2_th13;

	//simplex[3] mass_simplex;
	//real<lower=0.0, upper=1.0> m_scale;

}


transformed parameters{

	//vector[3] nu_mass;

	real<lower=-2, upper=2> delta_m32_with_sign;	   // Sign indicates prefered hierarchy
	real<lower=0.0> min_mass;
	vector<lower=0.0>[3] Ue_squared;   // Squares of PMNS matrix elements U_e
	real delta_m21;
	real delta_m13;
	real<lower=0.0> delta_m32;

	real m_beta_squared;
	real m_beta;
	real m_s;

	//nu_mass = mass_simplex*m_scale;

	delta_m21 = square(nu_mass[2]) - square(nu_mass[1]);
	delta_m13 = square(nu_mass[3]) - square(nu_mass[1]);
	delta_m32 = sqrt(square(square(nu_mass[3]) - square(nu_mass[2])));
	
	delta_m32_with_sign = square(nu_mass[3]) - square(nu_mass[2]);
	min_mass = min(nu_mass);
	Ue_squared = get_U_PMNS(nFamily(), sin2_th12, sin2_th13);
	
	m_beta_squared = get_effective_mass_squared(Ue_squared, nu_mass);

	if (m_beta_squared<0.){
		m_beta = -1.*pow(fabs(m_beta_squared), 0.5);
		print("m_beta");

	}
	else{
		m_beta = pow(m_beta_squared, 0.5);
	}

	m_s = sum(nu_mass);
}


model{

	sin2_th12_means ~ normal(sin2_th12, sin2_th12_sigmas);
	sin2_th13_means ~ normal(sin2_th13, sin2_th13_sigmas);
	delta_m21_means ~ normal(delta_m21, delta_m21_sigmas);

	
	if (nu_mass[2] < nu_mass[3]){
	   delta_m32_means_NH ~ normal(delta_m32_with_sign, delta_m32_sigmas_NH);
	   sin2_th13_means_NH ~ normal(sin2_th13, sin2_th13_sigmas_NH);
	   }
	else if (nu_mass[3] < nu_mass[2]){
	   delta_m32_means_IH ~ normal(delta_m32_with_sign, delta_m32_sigmas_IH);
	   sin2_th13_means_IH ~ normal(sin2_th13, sin2_th13_sigmas_IH);
	}


	if (use_m_beta == 1){
	   m_beta_squared_mean ~ normal(m_beta_squared, m_beta_squared_sigma);
	   }
	if (use_m_s == 1){
	   m_s_mean ~ normal(m_s, m_s_sigma);
	   }


}
