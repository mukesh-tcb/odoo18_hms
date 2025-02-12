// /** @odoo-module **/

// // import { registry } from "@web/core/registry";
// // import { useService } from "@web/core/utils/hooks";
// // const { Component, useState, onWillStart, onWillUpdateProps, onWillUnmount } = owl;

// // function formatTime(startTime, endTime = null) {
// //     const start = new Date(startTime);
// //     const end = endTime ? new Date(endTime) : new Date();
// //     const diff = end - start;

// //     const hours = Math.floor(diff / 3600000);
// //     const minutes = Math.floor((diff % 3600000) / 60000);
// //     const seconds = Math.floor((diff % 60000) / 1000);

// //     return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
// // }

// // class DilationTimer extends Component {
// //     setup() {
// //         this.orm = useService("orm");
// //         this.state = useState({
// //             duration: this.props.value || "00:00:00",
// //             isRunning: this.props.record.data.is_dilation_running,
// //         });
// //         this.intervalId = null;

// //         onWillStart(async () => {
// //             if (this.state.isRunning) {
// //                 await this.updateDuration();
// //                 this.startInterval();
// //             }
// //         });

// //         onWillUpdateProps(async (nextProps) => {
// //             const newIsRunning = nextProps.record.data.is_dilation_running;
// //             if (newIsRunning !== this.state.isRunning) {
// //                 this.state.isRunning = newIsRunning;
// //                 if (newIsRunning) {
// //                     await this.updateDuration();
// //                     this.startInterval();
// //                 } else {
// //                     this.stopInterval();
// //                 }
// //             }
// //         });

// //         onWillUnmount(() => {
// //             this.stopInterval();
// //         });
// //     }

// //     startInterval() {
// //         if (!this.intervalId) {
// //             this.intervalId = setInterval(async () => {
// //                 if (this.state.isRunning) {
// //                     await this.updateDuration();
// //                 }
// //             }, 1000);
// //         }
// //     }

// //     stopInterval() {
// //         if (this.intervalId) {
// //             clearInterval(this.intervalId);
// //             this.intervalId = null;
// //         }
// //     }

// //     async updateDuration() {
// //         const record = await this.orm.read(
// //             "tcb.ophthalmology.evaluation",
// //             [this.props.record.resId],
// //             ["dilation_start_time", "dilation_end_time"]
// //         );

// //         if (record && record[0]) {
// //             const startTime = record[0].dilation_start_time;
// //             const endTime = record[0].dilation_end_time;
// //             this.state.duration = formatTime(startTime, endTime);
// //         }
// //     }

// //     async onStartClick() {
// //         await this.orm.call(
// //             "tcb.ophthalmology.evaluation",
// //             "action_start_dilation",
// //             [[this.props.record.resId]]
// //         );
// //         this.props.record.model.load();
// //     }

// //     async onStopClick() {
// //         await this.orm.call(
// //             "tcb.ophthalmology.evaluation",
// //             "action_end_dilation",
// //             [[this.props.record.resId]]
// //         );
// //         this.props.record.model.load();
// //     }

// //     async onResetClick() {
// //         await this.orm.call(
// //             "tcb.ophthalmology.evaluation",
// //             "reset_dilation_process",
// //             [[this.props.record.resId]]
// //         );
// //         this.props.record.model.load();
// //     }
// // }


// // DilationTimer.supportedTypes = ["char"];

// // registry.category("fields").add("dilation_timer", DilationTimer);

// let startBtn = document.querySelector('button[name="action_start_dilation"]');
// // let stopBtn = document.getElementById('stop');
// // let resetBtn = document.getElementById('reset');

// let hour = 0;
// let minute = 0;
// let second = 0;
// let count = 0;

// startBtn.addEventListener('click', function () {
//     timer = true;
//     stopWatch();
// });

// // stopBtn.addEventListener('click', function () {
// //     timer = false;
// // });

// // resetBtn.addEventListener('click', function () {
// //     timer = false;
// //     hour = 0;
// //     minute = 0;
// //     second = 0;
// //     count = 0;
// //     document.getElementById('hr').innerHTML = "00";
// //     document.getElementById('min').innerHTML = "00";
// //     document.getElementById('sec').innerHTML = "00";
// //     document.getElementById('count').innerHTML = "00";
// // });

// // function stopWatch() {
// //     if (timer) {
// //         count++;

// //         if (count == 100) {
// //             second++;
// //             count = 0;
// //         }

// //         if (second == 60) {
// //             minute++;
// //             second = 0;
// //         }

// //         if (minute == 60) {
// //             hour++;
// //             minute = 0;
// //             second = 0;
// //         }

// //         let hrString = hour;
// //         let minString = minute;
// //         let secString = second;
// //         let countString = count;

// //         if (hour < 10) {
// //             hrString = "0" + hrString;
// //         }

// //         if (minute < 10) {
// //             minString = "0" + minString;
// //         }

// //         if (second < 10) {
// //             secString = "0" + secString;
// //         }

// //         if (count < 10) {
// //             countString = "0" + countString;
// //         }

// //         document.getElementById('hr').innerHTML = hrString;
// //         document.getElementById('min').innerHTML = minString;
// //         document.getElementById('sec').innerHTML = secString;
// //         document.getElementById('count').innerHTML = countString;
// //         setTimeout(stopWatch, 10);
// //     }
// // }


// function stopWatch() {
//     console.log("wah")
// }


/** @odoo-module **/
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

const { Component, useState, onWillStart, onWillUpdateProps, onWillUnmount } = owl;

function formatMinutes(value) {
    if (value === false || value === undefined) {
        return "00:00";
    }
    const totalSeconds = Math.round(value * 60);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

class DilationTimer extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            duration: this.props.value || 0,
        });

        this.intervalId = null;

        onWillStart(async () => {
            if (this.props.record.data.is_dilation_running) {
                await this.updateDuration();
                this.startInterval();
            }
            $('#custom_open_draw_canvas_2').click(function(e) {
                 e.preventDefault();
                setupCanvas();
                $('#custom_draw_image_2').show()
            });
        });

        onWillUpdateProps(async (nextProps) => {
            if (nextProps.record.data.is_dilation_running !== this.props.record.data.is_dilation_running) {
                if (nextProps.record.data.is_dilation_running) {
                    await this.updateDuration();
                    this.startInterval();
                } else {
                    this.stopInterval();
                    this.state.duration = nextProps.value || 0;
                }
            }
        });

        onWillUnmount(() => {
            this.stopInterval();
        });
    }

    startInterval() {
        if (!this.intervalId) {
            this.intervalId = setInterval(async () => {
                if (this.props.record.data.is_dilation_running) {
                    await this.updateDuration();
                }
            }, 1000);
        }
    }

    stopInterval() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }

    async updateDuration() {
        const duration = await this.orm.call(
            this.props.record.resModel,
            'get_current_duration',
            [this.props.record.resId]
        );
        this.state.duration = duration;
    }

    get formattedDuration() {
        return formatMinutes(this.state.duration);
    }
}

DilationTimer.template = 'web.DilationTimer';
DilationTimer.supportedTypes = ["float"];

registry.category("fields").add("dilation_timer", DilationTimer);