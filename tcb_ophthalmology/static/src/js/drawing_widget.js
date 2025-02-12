/** @odoo-module **/

import { AbstractField } from "@web/core/views/fields";
import { fieldRegistry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { Component } from "@odoo/owl";

class DrawingWidget extends AbstractField {
    static template = "tcb_ophthalmology.DrawingWidgetTemplate";
    
    static events = {
        'click .js-copy-image': '_copyImageToCanvas',
        'click .js-undo': '_undo',
        'click .js-clear': '_clearCanvas',
        'click .js-save': '_saveDrawing',
        'mousedown .drawing-canvas': '_startDrawing',
        'mousemove .drawing-canvas': '_draw',
        'mouseup .drawing-canvas': '_stopDrawing',
        'mouseleave .drawing-canvas': '_stopDrawing',
    };

    setup() {
        super.setup();
        this.defaultImage = null;
        this.isModified = false;
        this.drawingHistory = [];
        this.currentHistoryIndex = -1;
        this.isDrawing = false;
        this.lastX = 0;
        this.lastY = 0;

        // Load the default image
        this._loadDefaultImage();
    }

    async _loadDefaultImage() {
        const img = new Image();
        img.crossOrigin = "Anonymous";
        img.src = '/tcb_ophthalmology/static/img/default_eye.png';
        img.onload = () => {
            const canvas = document.createElement('canvas');
            canvas.width = img.width;
            canvas.height = img.height;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0);
            this.defaultImage = canvas.toDataURL();
            this._render();
        };
    }

    _render() {
        const canvas = this.el.querySelector('.drawing-canvas');
        const ctx = canvas.getContext('2d');

        const img = new Image();
        img.onload = () => {
            canvas.width = img.width;
            canvas.height = img.height;
            ctx.drawImage(img, 0, 0);

            if (this.value) {
                const savedImg = new Image();
                savedImg.onload = () => ctx.drawImage(savedImg, 0, 0);
                savedImg.src = `data:image/png;base64,${this.value}`;
                this.isModified = true;
            }
        };
        img.src = this.defaultImage;
    }

    _startDrawing(e) {
        this.isDrawing = true;
        const rect = e.target.getBoundingClientRect();
        [this.lastX, this.lastY] = [e.clientX - rect.left, e.clientY - rect.top];
        this._pushToHistory();
    }

    _draw(e) {
        if (!this.isDrawing) return;
        const canvas = e.target;
        const ctx = canvas.getContext('2d');
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        ctx.beginPath();
        ctx.moveTo(this.lastX, this.lastY);
        ctx.lineTo(x, y);
        ctx.strokeStyle = '#ff0000';
        ctx.lineWidth = 2;
        ctx.stroke();

        [this.lastX, this.lastY] = [x, y];
        this.isModified = true;
    }

    _stopDrawing() {
        this.isDrawing = false;
    }

    _pushToHistory() {
        if (this.currentHistoryIndex < this.drawingHistory.length - 1) {
            this.drawingHistory = this.drawingHistory.slice(0, this.currentHistoryIndex + 1);
        }
        const canvas = this.el.querySelector('.drawing-canvas');
        this.drawingHistory.push(canvas.toDataURL());
        this.currentHistoryIndex++;
    }

    _undo() {
        if (this.currentHistoryIndex > 0) {
            this.currentHistoryIndex--;
            const img = new Image();
            img.onload = () => {
                const canvas = this.el.querySelector('.drawing-canvas');
                const ctx = canvas.getContext('2d');
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(img, 0, 0);
            };
            img.src = this.drawingHistory[this.currentHistoryIndex];
            this.isModified = true;
        }
    }

    _clearCanvas() {
        const canvas = this.el.querySelector('.drawing-canvas');
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        const img = new Image();
        img.src = this.defaultImage;
        img.onload = () => ctx.drawImage(img, 0, 0);
        this.drawingHistory = [];
        this.currentHistoryIndex = -1;
        this.isModified = false;
    }

    _copyImageToCanvas() {
        const canvas = this.el.querySelector('.drawing-canvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();
        img.src = this.defaultImage;
        img.onload = () => {
            ctx.drawImage(img, 0, 0);
            this._pushToHistory();
            this.isModified = true;
        };
    }

    _saveDrawing() {
        if (!this.isModified) {
            this.do_warn(_t("No changes to save."));
            return;
        }

        const canvas = this.el.querySelector('.drawing-canvas');
        const dataURL = canvas.toDataURL('image/png');
        const base64Data = dataURL.split(',')[1];

        if (base64Data === this.defaultImage.split(',')[1]) {
            this.do_warn(_t("No changes to save."));
            return;
        }

        this.trigger_up('field_changed', {
            dataPointID: this.dataPointID,
            changes: { [this.name]: base64Data },
        });
        this.isModified = false;
    }
}

fieldRegistry.add('drawing_widget', DrawingWidget);