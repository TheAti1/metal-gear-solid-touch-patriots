// SPDX-License-Identifier: MIT
using System;
using System.Windows.Input;
internal static class TouchKeyNames {
    public static string For(Key key){
        string name=key.ToString();
        if(name.Length==2&&name[0]=='D'&&Char.IsDigit(name[1]))return name.Substring(1);
        if(name.StartsWith("NumPad"))return "Keypad "+name.Substring(6);
        switch(key){
        case Key.Enter:return "Return";case Key.Back:return "Backspace";case Key.Space:return "Space";
        case Key.LeftCtrl:return "Left Ctrl";case Key.RightCtrl:return "Right Ctrl";
        case Key.LeftShift:return "Left Shift";case Key.RightShift:return "Right Shift";
        case Key.LeftAlt:return "Left Alt";case Key.RightAlt:return "Right Alt";
        case Key.CapsLock:return "CapsLock";case Key.OemMinus:return "-";case Key.OemPlus:return "=";
        case Key.OemOpenBrackets:return "[";case Key.OemCloseBrackets:return "]";case Key.OemPipe:return "\\";
        case Key.OemSemicolon:return ";";case Key.OemQuotes:return "'";case Key.OemComma:return ",";
        case Key.OemPeriod:return ".";case Key.OemQuestion:return "/";case Key.OemTilde:return "`";
        case Key.Add:return "Keypad +";case Key.Subtract:return "Keypad -";case Key.Multiply:return "Keypad *";case Key.Divide:return "Keypad /";
        default:return name;
        }
    }
}
