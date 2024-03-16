import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { HeaderComponent } from './header/header.component';
import { ChatService } from './chat.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, FormsModule, CommonModule, HeaderComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  messages: string[] = [];

  currentMsg: string = '';
  constructor(private chsrv: ChatService){
  }
  ngOnInit(){
    this.chsrv.init('ws://127.0.0.1:8000/chat/1')
    this.chsrv.messages$?.subscribe({
      next: (data) => this.messages = data,
      error: () => "An Error Occured"
    });

  }

  sendMsg(){
    this.chsrv.sendMsg(this.currentMsg);
    this.currentMsg = '';
  }


  title = 'bot';
  dark = false;
  toggleColor = () => {
    this.dark = !this.dark;
  }
}
