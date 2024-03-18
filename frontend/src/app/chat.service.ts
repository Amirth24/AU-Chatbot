import { Injectable } from '@angular/core';
import {Subject, connect} from 'rxjs'


enum MessageFrom {
  AI = "AI",
  HUMAN = "HUMAN"
}
export interface Message {
  by: MessageFrom,
  content: string
}

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private socket: WebSocket | null = null;
  public messages$: Subject<Message> = new Subject();
  public live$: Subject<boolean> = new Subject();
  private _currentMessage: string = "";
  constructor() {}
  connect(url: string){
    this.socket = new WebSocket(url);
  }
  init(url: string) {
    this.connect(url);
    if (this.socket !== null){
      this.socket.onopen = () => {
        this.live$.next(true);
      }

      this.socket.onclose = () => {
        this.live$.next(true);
      }
      this.socket.onmessage = (e) => {
        console.log(e.data);
        this._currentMessage += e.data;
        if (this._currentMessage.endsWith('[END]')){
          this.messages$.next({
            by: MessageFrom.AI,
            content: this._currentMessage.slice(0, -5)
          })
          this._currentMessage="";
        }
      }
    }

  }

  sendMsg(mess: string){
    this.socket?.send(mess);
    this.messages$.next({
      by: MessageFrom.HUMAN,
      content: mess
    })
    console.log("Message Sent " + mess);
  }
}
