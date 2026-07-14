"use strict";

const fieldlist_item_selector = 'div[role="group"]';

function addFieldListItem(event) {
    const btn = event.target.closest('button');
    const fieldlist = btn.closest(".fieldlist")
    const template = fieldlist.querySelector('.fieldlist-prototype');
    const container = fieldlist.querySelector('.fieldlist-items');
    const clone = template.content.cloneNode(true);

    // get the last index value/count
    const index = container.querySelectorAll(fieldlist_item_selector).length;

    clone.querySelectorAll('[data-name-template]').forEach(function(element) {
        const template = element.dataset.nameTemplate;
        console.log(template);
        const new_name = template.replaceAll('{__index__}', index)
        console.log(new_name);
        element.name = new_name
    });

    container.appendChild(clone);

    // select the new input
    const new_input = container.querySelector('input[' + new_input + ']')
    if (new_input) {
        new_input.focus();
    }
}

function removeFieldListRow(event) {
    const btn = event.target.closest('button');
    const row = btn.closest(fieldlist_item_selector);
    if (row) {
        row.remove();
    }
}

document.addEventListener('DOMContentLoaded', function () {
    document.addEventListener('click', function (event) {
        /* Click element like a link */
        var row = event.target.closest('[data-href]');
        if (!row) return;

        window.location = row.getAttribute('data-href');
    });

    flatpickr('input[type=datetime]', {
        enableTime: true,
        dateFormat: 'Y-m-d H:i',
        time_24hr: true,
    });
});
