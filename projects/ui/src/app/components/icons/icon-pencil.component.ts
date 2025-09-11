import { Component } from '@angular/core';

@Component({
  selector: 'app-icon-pencil',
  standalone: true,
  template: `
    <svg width="16" height="16" viewBox="0 0 24 24" class="icon">
      <path
        d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="m15 5 4 4"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    </svg>
  `,
  styles: [
    `
      .icon {
        display: inline-block;
        vertical-align: middle;
      }
    `,
  ],
})
export class IconPencilComponent {}
