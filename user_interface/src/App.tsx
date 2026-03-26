import './index.css';
import { IpInputField } from './components/IpInputField';
import { IPCheckList } from './components/IPCheckList';

function App() {
  return (
    <div className="app-container">
      <div className="glass-card">
        <h1 className="title">IP checker</h1>
        <p className="subtitle">Enter an IP address to check</p>
        <IpInputField />
        <IPCheckList />
      </div>
    </div>
  );
}

export default App;
