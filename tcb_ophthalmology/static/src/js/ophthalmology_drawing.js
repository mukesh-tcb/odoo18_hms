/** @odoo-module */

import { FormController } from '@web/views/form/form_controller';
import { patch } from "@web/core/utils/patch";

patch(FormController.prototype, 'tcb_ophthalmology', {
    setup() {
        this._super();
        if (this.props.resModel=='tcb.ophthalmology.evaluation'){
            this.onNotebookPageChange = (notebookId, page) => {
//                if(page == 'page_5'){
                    $('#custom_open_draw_canvas').click(function(e) {
                         e.preventDefault();
                        setupCanvas();
                        $('#custom_draw_image').show()
                    });
//                }
            };
        }
    }
});