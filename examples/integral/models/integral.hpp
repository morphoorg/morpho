inline double calculate_integral(double threshold, std::ostream* pstream) {
	/* Read the spectrum and normalize. */
	TFile* file = new TFile("integral/models/model_input/spectrum.root", "READ");
	TH1D* spectrum = (TH1D*)file->Get("th");
	spectrum->Scale(1/spectrum->Integral());
	int low = spectrum->FindBin(threshold);
	int up = spectrum->GetNbinsX();
	double integral = spectrum->Integral(low, up);
	delete spectrum;
	file->Close();
	delete file;
	return integral;
}

inline double calculate_derivative(double (*y)(double, std::ostream*), double x, double precision, std::ostream* pstream) {
	/* The derivative, which is required by Stan, should be given by users. */
	/* An example to calculate derivative using Richardson's extrapolation method. */
	double h = precision;
	double D_1 = (y(x+h, pstream) - y(x-h, pstream))/2./h;
	double D_2 = (y(x+h/2, pstream) - y(x-h/2, pstream))/h;
	return (4. * D_2 - D_1) / 3.;
}
	

inline var calculate_integral(const var& threshold_var, std::ostream* pstream) {
	double threshold = threshold_var.val();
	double integral = calculate_integral(threshold, pstream);
	/* Since our threshold is fixed, the derivative will not affect sampling and can be any value. */
	double derivative = calculate_derivative(calculate_integral, threshold, 200, pstream);
	return var(new precomp_v_vari(integral, threshold_var.vi_, derivative));
}



