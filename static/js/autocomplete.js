'use strict';

// searchBox        = query selector string
// urlBuilder       = function that returns the url the request should be sent to
// selectCallback   = function to be called when a candidate is selected   (optional, can be null)
// deselectCallback = function to be called when a candidate is deselected (optional, can be null)
class Autocomplete {
    constructor(searchBox, urlBuilder, selectCallback, deselectCallback) {
        this.searchBox = searchBox;
        
        if (this.searchBox !== null) {
            this.searchBox.setAttribute("autocomplete", "off")
            
            this.candidateList = document.createElement("div")
            this.candidateList.setAttribute("class", "autocomplete");
            this.searchBox.parentNode.appendChild(this.candidateList);
            
            this.selectCallback   = selectCallback;
            this.deselectCallback = deselectCallback;
            
            this.urlBuilder = urlBuilder;
            
            this.searchBox.oninput   = () => this.oninput();
            this.searchBox.onblur    =  e => this.onblur(e);
            this.searchBox.onfocus   = () => this.onfocus();
            this.searchBox.onkeydown =  e => this.onkeydown(e);
        }
    }
    
    selectCandidate(candidate) {
        // Call the callback.
        if (this.selectCallback !== null) {
            this.selectCallback(candidate.getAttribute("pk"), candidate.getAttribute("url"));
        }
        
        // Set the contents of the search box to the candidate clicked.
        this.searchBox.value = candidate.textContent;
        
        // Highlight the search box to indicate that a candidate is locked in.
        this.searchBox.setAttribute("class", "highlighted");
        
        // Remove the highlight class from the autocomplete candidate we just selected.
        candidate.setAttribute("class", "item");
        
        // Hide the autocomplete box.
        this.candidateList.style.display = "none";
    }
    
    deselectCandidate() {
        this.searchBox.setAttribute("class", "");
        
        // Call the callback.
        if (this.deselectCallback !== null) {
            this.deselectCallback();
        }
    }
    
    oninput() {
        // Cancel any old request, since the user has pressed a new key and invalidated the old input.
        Autocomplete.request.abort();
        this.deselectCandidate();
        
        let url = this.urlBuilder();
        
        // If the URL builder returned an URL and there are more than 3 characters in the input, open a new request.
        if (this.searchBox.value.length >= 3 && url !== "") {
            Autocomplete.request.onload = () => this.onload();
            Autocomplete.request.open("GET", url + this.searchBox.value);
            Autocomplete.request.send();
        }
        // Else, hide the autocomplete box and remove old candidates.
        else {
            this.candidateList.style.display = "none";
            
            while (this.candidateList.firstChild) {
                this.candidateList.firstChild.remove();
            }
        }
    }
    
    onblur(e) {
        if (this.candidateList.matches(":hover") === true) {
            this.searchBox.focus();
            return false;
        }
        else {
            this.candidateList.style.display = "none";
        }
        
    }
    
    onfocus() {
        if (this.candidateList.firstChild) {
            this.candidateList.style.display = "block";
        }
    }
    
    onclick(e, candidate) {
        this.selectCandidate(candidate);
        return false;
    }
    
    onkeydown(e) {
        // If there are autocomplete candidates.
        if (this.candidateList.firstChild) {
            // Up or down key
            if (e.keyCode === 40 || e.keyCode === 38) {
                let currentNode = this.candidateList.querySelector(".highlighted");
                
                if (currentNode !== null) {
                    currentNode.setAttribute("class", "item");
                    var nextNode = (e.keyCode === 38 ? currentNode.previousSibling : currentNode.nextSibling)
                }
                
                if (currentNode === null || nextNode === null) {
                    var nextNode = (e.keyCode === 38 ? this.candidateList.lastChild : this.candidateList.firstChild)
                }
                
                nextNode.setAttribute("class", "item highlighted");
            }
            
            // Enter key
            if (e.keyCode === 13) {
                let highlightedNode = this.candidateList.querySelector(".highlighted");
                
                if (highlightedNode !== null) {
                    this.selectCandidate(highlightedNode);
                    e.preventDefault();
                }
            }
            
            // Escape key
            if (e.keyCode === 27) {
                this.candidateList.style.display = "none";
            }
        }
    }
    
    onload() {
        if (Autocomplete.request.response !== null) {
            // Remove any old autocomplete candidates from the DOM.
            while (this.candidateList.firstChild) {
                this.candidateList.firstChild.remove();
            }
            
            // Populate the DOM with new autocomplete candidates.
            for (let i = 0; i < Autocomplete.request.response["results"].length; i++) {
                let candidate = document.createElement("div");
                candidate.setAttribute("class", "item");
                candidate.setAttribute("pk",  Autocomplete.request.response["results"][i][0]);
                candidate.textContent       = Autocomplete.request.response["results"][i][1];
                candidate.setAttribute("url", Autocomplete.request.response["results"][i][2]);
                candidate.onclick = e => this.onclick(e, candidate)
                
                this.candidateList.appendChild(candidate);
            }
            
            // Display the autocomplete box.
            this.candidateList.style.display = "block";
        }
    }
}

Autocomplete.request = new XMLHttpRequest();
Autocomplete.request.responseType = "json";
