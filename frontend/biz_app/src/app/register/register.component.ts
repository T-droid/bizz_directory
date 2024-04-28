import { Component } from '@angular/core';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrl: './register.component.css'
})
export class RegisterComponent {
  username: string = '';
  email: string = '';
  password: string = '';
  confirmpassword: string = '';

  register(): void {
    if (this.password !== this.confirmpassword) {
      // Passwords do not match, handle error (e.g., display error message)
      console.error("Passwords do not match");
      return;
      }
      console.log('Username:', this.username);
      console.log('Email:', this.email);
      console.log('Password:', this.password);
      console.log('Confirm Password:', this.confirmpassword);
    }
  }
