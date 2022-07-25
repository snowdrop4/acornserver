'use strict';

class Autofill {
	constructor(selectBox, urlBuilder, selectCallback, deselectCallback) {
		this.selectBox = selectBox;
		this.selectBox.onchange = () => this.onchange();
		
		this.selectCallback   = selectCallback;
		this.deselectCallback = deselectCallback;
		
		this.urlBuilder = urlBuilder;
	}
	
	onchange() {
		// Cancel any old request, since the user has invalidated the old selection.
		Autofill.request.abort();
		
		if (this.selectBox.value !== "") {
			let url = this.urlBuilder(this.selectBox.value);
			
			if (url !== "") {
				Autofill.request.onload = () => this.onload();
				Autofill.request.open("GET", url);
				Autofill.request.send();
			}
		}
		else {
			this.deselectCallback();
		}
	}
	
	onload() {
		if (Autofill.request.response !== null) {
			this.selectCallback(Autofill.request.response);
		}
	}
	
	add_option(val, text) {
		let option = document.createElement("option");
		option.value = val;
		option.textContent = text;
		this.selectBox.appendChild(option);
	}
	
	clear_options() {
		// Remove all options.
		while (this.selectBox.firstChild) {
			this.selectBox.firstChild.remove();
		}
		
		// Create the blank option.
		let option = document.createElement("option");
		option.value = "";
		option.textContent = "---------";
		this.selectBox.appendChild(option);
		this.selectBox.value = "";
		
		// Call the deselect callback (since we remove all the options this is the same as the user deselecting one)
		this.deselectCallback();
	}
}

Autofill.request = new XMLHttpRequest();
Autofill.request.responseType = "json";
