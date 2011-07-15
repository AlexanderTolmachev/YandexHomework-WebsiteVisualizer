function tree_toggle(event) {
	event = event || window.event
	var clickedElem = event.target || event.srcElement

    // If ckick is not in right plase
	if (!hasClass(clickedElem, 'Expand')) {
		return 
	}

    // Select clicked node
	var node = clickedElem.parentNode
	// If clicked node is leaf
    if (hasClass(node, 'ExpandLeaf')) {
		return 
	}

	// Sefine new class for a node
	var newClass = hasClass(node, 'ExpandOpen') ? 'ExpandClosed' : 'ExpandOpen'
	// Change current node class to newClass
	var re =  /(^|\s)(ExpandOpen|ExpandClosed)(\s|$)/
	node.className = node.className.replace(re, '$1'+newClass+'$3')
}


function hasClass(elem, className) {
	return new RegExp("(^|\\s)"+className+"(\\s|$)").test(elem.className)
}

