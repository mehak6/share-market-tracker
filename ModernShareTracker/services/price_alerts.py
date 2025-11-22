"""
Real-time Price Alerts System
Advanced price monitoring and notification system with multiple alert types
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from enum import Enum
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import requests
# import websocket  # Optional - for real-time WebSocket connections
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertType(Enum):
    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    PERCENTAGE_GAIN = "percentage_gain"
    PERCENTAGE_LOSS = "percentage_loss"
    VOLUME_SPIKE = "volume_spike"
    MOVING_AVERAGE = "moving_average"
    SUPPORT_RESISTANCE = "support_resistance"
    NEWS_SENTIMENT = "news_sentiment"


class NotificationChannel(Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push_notification"
    POPUP = "popup"
    SOUND = "sound"
    WEBHOOK = "webhook"


@dataclass
class PriceAlert:
    id: str
    user_id: str
    symbol: str
    alert_type: AlertType
    condition_value: float
    current_price: float
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool = True
    notification_channels: List[NotificationChannel] = None
    triggered: bool = False
    triggered_at: Optional[datetime] = None
    message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.notification_channels is None:
            self.notification_channels = [NotificationChannel.POPUP]


@dataclass
class MarketData:
    symbol: str
    price: float
    volume: int
    change: float
    change_percent: float
    timestamp: datetime
    high_52w: Optional[float] = None
    low_52w: Optional[float] = None
    market_cap: Optional[float] = None


class RealTimePriceAlertsSystem:
    """Advanced real-time price alerts system"""
    
    def __init__(self):
        self.alerts: Dict[str, PriceAlert] = {}
        self.market_data: Dict[str, MarketData] = {}
        self.websocket_connections: Dict[str, websocket.WebSocket] = {}
        self.notification_handlers: Dict[NotificationChannel, Callable] = {}
        self.is_running = False
        self.price_update_callbacks: List[Callable] = []
        self.alert_history: List[PriceAlert] = []
        
        # Initialize notification handlers
        self._setup_notification_handlers()
        
        # Email configuration
        self.smtp_config = {
            'server': 'smtp.gmail.com',
            'port': 587,
            'username': '',
            'password': '',
            'from_email': ''
        }
    
    def _setup_notification_handlers(self):
        """Setup notification handlers for different channels"""
        self.notification_handlers = {
            NotificationChannel.EMAIL: self._send_email_notification,
            NotificationChannel.SMS: self._send_sms_notification,
            NotificationChannel.PUSH: self._send_push_notification,
            NotificationChannel.POPUP: self._show_popup_notification,
            NotificationChannel.SOUND: self._play_sound_notification,
            NotificationChannel.WEBHOOK: self._send_webhook_notification
        }
    
    async def create_alert(
        self,
        user_id: str,
        symbol: str,
        alert_type: AlertType,
        condition_value: float,
        notification_channels: List[NotificationChannel] = None,
        expires_in_hours: int = 24,
        message: str = None
    ) -> str:
        """Create a new price alert"""
        
        alert_id = f"{user_id}_{symbol}_{int(datetime.now().timestamp())}"
        expires_at = datetime.now() + timedelta(hours=expires_in_hours)
        
        # Get current price
        current_price = await self._get_current_price(symbol)
        
        alert = PriceAlert(
            id=alert_id,
            user_id=user_id,
            symbol=symbol.upper(),
            alert_type=alert_type,
            condition_value=condition_value,
            current_price=current_price,
            created_at=datetime.now(),
            expires_at=expires_at,
            notification_channels=notification_channels or [NotificationChannel.POPUP],
            message=message
        )
        
        self.alerts[alert_id] = alert
        
        # Start monitoring this symbol if not already
        await self._start_monitoring_symbol(symbol)
        
        logger.info(f"Created alert {alert_id} for {symbol} - {alert_type.value}: {condition_value}")
        return alert_id
    
    async def create_smart_alerts(self, user_id: str, portfolio: Dict) -> List[str]:
        """Create intelligent alerts based on portfolio analysis"""
        
        alert_ids = []
        
        for stock in portfolio.get('stocks', []):
            symbol = stock['symbol']
            current_price = stock.get('current_price', 0)
            purchase_price = stock.get('purchase_price', 0)
            
            if current_price > 0 and purchase_price > 0:
                # Stop-loss alert (5% below current price)
                stop_loss_price = current_price * 0.95
                alert_id = await self.create_alert(
                    user_id, symbol, AlertType.PRICE_BELOW, stop_loss_price,
                    [NotificationChannel.EMAIL, NotificationChannel.POPUP],
                    message=f"Stop-loss triggered for {symbol}"
                )
                alert_ids.append(alert_id)
                
                # Profit target alert (10% above current price)
                profit_target = current_price * 1.10
                alert_id = await self.create_alert(
                    user_id, symbol, AlertType.PRICE_ABOVE, profit_target,
                    [NotificationChannel.POPUP],
                    message=f"Profit target reached for {symbol}"
                )
                alert_ids.append(alert_id)
                
                # High gain/loss alerts
                gain_loss_percent = ((current_price - purchase_price) / purchase_price) * 100
                
                if gain_loss_percent > 20:  # High gain alert
                    alert_id = await self.create_alert(
                        user_id, symbol, AlertType.PERCENTAGE_GAIN, 25,
                        [NotificationChannel.EMAIL],
                        message=f"Consider booking profits in {symbol}"
                    )
                    alert_ids.append(alert_id)
                
                elif gain_loss_percent < -10:  # High loss alert
                    alert_id = await self.create_alert(
                        user_id, symbol, AlertType.PERCENTAGE_LOSS, -15,
                        [NotificationChannel.EMAIL, NotificationChannel.POPUP],
                        message=f"Significant loss in {symbol} - review position"
                    )
                    alert_ids.append(alert_id)
        
        return alert_ids
    
    async def _start_monitoring_symbol(self, symbol: str):
        """Start real-time monitoring for a symbol"""
        if symbol not in self.websocket_connections:
            # In production, connect to real WebSocket feeds
            # For now, simulate with periodic updates
            asyncio.create_task(self._simulate_price_updates(symbol))
    
    async def _simulate_price_updates(self, symbol: str):
        """Simulate real-time price updates (replace with actual WebSocket)"""
        while symbol in [alert.symbol for alert in self.alerts.values() if alert.is_active]:
            try:
                # Get current price (mock data)
                new_price = await self._get_current_price(symbol)
                
                # Update market data
                self.market_data[symbol] = MarketData(
                    symbol=symbol,
                    price=new_price,
                    volume=100000,  # Mock volume
                    change=0.5,
                    change_percent=0.5,
                    timestamp=datetime.now()
                )
                
                # Check alerts for this symbol
                await self._check_alerts_for_symbol(symbol, new_price)
                
                # Notify callbacks
                for callback in self.price_update_callbacks:
                    await callback(symbol, new_price)
                
                await asyncio.sleep(10)  # Update every 10 seconds
                
            except Exception as e:
                logger.error(f"Error updating price for {symbol}: {e}")
                await asyncio.sleep(30)  # Retry after 30 seconds
    
    async def _check_alerts_for_symbol(self, symbol: str, current_price: float):
        """Check all alerts for a specific symbol"""
        
        for alert in list(self.alerts.values()):
            if alert.symbol == symbol and alert.is_active and not alert.triggered:
                
                # Check if alert should trigger
                should_trigger = await self._should_trigger_alert(alert, current_price)
                
                if should_trigger:
                    await self._trigger_alert(alert, current_price)
    
    async def _should_trigger_alert(self, alert: PriceAlert, current_price: float) -> bool:
        """Check if an alert should trigger based on current conditions"""
        
        if alert.alert_type == AlertType.PRICE_ABOVE:
            return current_price >= alert.condition_value
        
        elif alert.alert_type == AlertType.PRICE_BELOW:
            return current_price <= alert.condition_value
        
        elif alert.alert_type == AlertType.PERCENTAGE_GAIN:
            if alert.current_price > 0:
                gain_percent = ((current_price - alert.current_price) / alert.current_price) * 100
                return gain_percent >= alert.condition_value
        
        elif alert.alert_type == AlertType.PERCENTAGE_LOSS:
            if alert.current_price > 0:
                loss_percent = ((current_price - alert.current_price) / alert.current_price) * 100
                return loss_percent <= alert.condition_value
        
        elif alert.alert_type == AlertType.VOLUME_SPIKE:
            # Check volume against historical average (simplified)
            return True  # Implement volume logic
        
        return False
    
    async def _trigger_alert(self, alert: PriceAlert, current_price: float):
        """Trigger an alert and send notifications"""
        
        alert.triggered = True
        alert.triggered_at = datetime.now()
        alert.is_active = False
        
        # Add to history
        self.alert_history.append(alert)
        
        # Prepare notification message
        message = self._format_alert_message(alert, current_price)
        
        # Send notifications through all specified channels
        for channel in alert.notification_channels:
            try:
                handler = self.notification_handlers.get(channel)
                if handler:
                    await handler(alert, message, current_price)
                else:
                    logger.warning(f"No handler found for notification channel: {channel}")
            except Exception as e:
                logger.error(f"Error sending notification via {channel}: {e}")
        
        logger.info(f"Alert triggered: {alert.id} - {message}")
    
    def _format_alert_message(self, alert: PriceAlert, current_price: float) -> str:
        """Format alert message for notifications"""
        
        if alert.message:
            return alert.message
        
        base_msg = f"🚨 PRICE ALERT: {alert.symbol}\n"
        
        if alert.alert_type == AlertType.PRICE_ABOVE:
            base_msg += f"Price reached ₹{current_price:.2f} (Target: ₹{alert.condition_value:.2f})"
        elif alert.alert_type == AlertType.PRICE_BELOW:
            base_msg += f"Price dropped to ₹{current_price:.2f} (Alert: ₹{alert.condition_value:.2f})"
        elif alert.alert_type == AlertType.PERCENTAGE_GAIN:
            gain = ((current_price - alert.current_price) / alert.current_price) * 100
            base_msg += f"Gained {gain:.1f}% - Now ₹{current_price:.2f}"
        elif alert.alert_type == AlertType.PERCENTAGE_LOSS:
            loss = ((current_price - alert.current_price) / alert.current_price) * 100
            base_msg += f"Lost {abs(loss):.1f}% - Now ₹{current_price:.2f}"
        
        base_msg += f"\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return base_msg
    
    # Notification handlers
    async def _send_email_notification(self, alert: PriceAlert, message: str, current_price: float):
        """Send email notification"""
        try:
            if not all([self.smtp_config['username'], self.smtp_config['password']]):
                logger.warning("Email credentials not configured")
                return
            
            msg = MimeMultipart()
            msg['From'] = self.smtp_config['from_email'] or self.smtp_config['username']
            msg['To'] = "user@example.com"  # Replace with actual user email
            msg['Subject'] = f"Price Alert: {alert.symbol}"
            
            # Enhanced HTML email
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                    <h2 style="color: #2c5aa0;">🚨 Price Alert Triggered</h2>
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0;">
                        <h3>{alert.symbol}</h3>
                        <p><strong>Current Price:</strong> ₹{current_price:.2f}</p>
                        <p><strong>Alert Type:</strong> {alert.alert_type.value.replace('_', ' ').title()}</p>
                        <p><strong>Condition:</strong> ₹{alert.condition_value:.2f}</p>
                        <p><strong>Time:</strong> {alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                    <p>{message}</p>
                    <hr>
                    <p style="font-size: 12px; color: #666;">
                        This is an automated alert from Modern Share Tracker.
                    </p>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MimeText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port']) as server:
                server.starttls()
                server.login(self.smtp_config['username'], self.smtp_config['password'])
                server.send_message(msg)
            
            logger.info(f"Email notification sent for alert {alert.id}")
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
    
    async def _send_sms_notification(self, alert: PriceAlert, message: str, current_price: float):
        """Send SMS notification (Twilio integration)"""
        # Implement SMS using Twilio or similar service
        logger.info(f"SMS notification would be sent: {message}")
    
    async def _send_push_notification(self, alert: PriceAlert, message: str, current_price: float):
        """Send push notification"""
        # Implement push notifications using FCM or similar
        logger.info(f"Push notification would be sent: {message}")
    
    async def _show_popup_notification(self, alert: PriceAlert, message: str, current_price: float):
        """Show desktop popup notification"""
        try:
            # For Windows
            import win32gui, win32con
            win32gui.MessageBox(0, message, f'Price Alert: {alert.symbol}', win32con.MB_OK)
        except ImportError:
            # Fallback for other platforms
            print(f"POPUP ALERT: {message}")
    
    async def _play_sound_notification(self, alert: PriceAlert, message: str, current_price: float):
        """Play sound notification"""
        try:
            import winsound
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except ImportError:
            print(f"SOUND ALERT: {message}")
    
    async def _send_webhook_notification(self, alert: PriceAlert, message: str, current_price: float):
        """Send webhook notification"""
        webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"  # Configure
        
        payload = {
            "text": f"Price Alert: {alert.symbol}",
            "attachments": [{
                "color": "warning",
                "fields": [
                    {"title": "Symbol", "value": alert.symbol, "short": True},
                    {"title": "Current Price", "value": f"₹{current_price:.2f}", "short": True},
                    {"title": "Alert Type", "value": alert.alert_type.value, "short": True},
                    {"title": "Condition", "value": f"₹{alert.condition_value:.2f}", "short": True}
                ]
            }]
        }
        
        try:
            response = requests.post(webhook_url, json=payload)
            if response.status_code == 200:
                logger.info(f"Webhook notification sent for alert {alert.id}")
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
    
    async def _get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol (mock implementation)"""
        # In production, integrate with real API like Yahoo Finance, Alpha Vantage, etc.
        
        # Mock price data with some volatility
        import random
        base_prices = {
            'RELIANCE': 2500,
            'TCS': 3200,
            'INFY': 1400,
            'HDFC': 1600,
            'WIPRO': 400,
            'ITC': 350,
            'SBIN': 500
        }
        
        base_price = base_prices.get(symbol.upper(), 1000)
        # Add random volatility (-2% to +2%)
        volatility = random.uniform(-0.02, 0.02)
        return base_price * (1 + volatility)
    
    def get_active_alerts(self, user_id: str = None) -> List[PriceAlert]:
        """Get all active alerts, optionally filtered by user"""
        alerts = [alert for alert in self.alerts.values() if alert.is_active]
        if user_id:
            alerts = [alert for alert in alerts if alert.user_id == user_id]
        return alerts
    
    def get_alert_history(self, user_id: str = None, limit: int = 50) -> List[PriceAlert]:
        """Get alert history"""
        history = self.alert_history
        if user_id:
            history = [alert for alert in history if alert.user_id == user_id]
        return history[:limit]
    
    def cancel_alert(self, alert_id: str) -> bool:
        """Cancel an active alert"""
        if alert_id in self.alerts:
            self.alerts[alert_id].is_active = False
            logger.info(f"Cancelled alert {alert_id}")
            return True
        return False
    
    def configure_email(self, smtp_server: str, port: int, username: str, password: str, from_email: str = None):
        """Configure email settings"""
        self.smtp_config.update({
            'server': smtp_server,
            'port': port,
            'username': username,
            'password': password,
            'from_email': from_email or username
        })
    
    def add_price_update_callback(self, callback: Callable):
        """Add callback for price updates"""
        self.price_update_callbacks.append(callback)
    
    async def start_monitoring(self):
        """Start the monitoring system"""
        self.is_running = True
        logger.info("Price alerts monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring system"""
        self.is_running = False
        logger.info("Price alerts monitoring stopped")
    
    def get_market_data(self, symbol: str) -> Optional[MarketData]:
        """Get current market data for a symbol"""
        return self.market_data.get(symbol.upper())
    
    def export_alerts_to_json(self) -> str:
        """Export all alerts to JSON"""
        alerts_data = {
            'active_alerts': [asdict(alert) for alert in self.get_active_alerts()],
            'alert_history': [asdict(alert) for alert in self.alert_history],
            'export_timestamp': datetime.now().isoformat()
        }
        return json.dumps(alerts_data, indent=2, default=str)


# Example usage and testing
async def test_price_alerts():
    """Test the price alerts system"""
    
    # Create alerts system
    alerts_system = RealTimePriceAlertsSystem()
    
    # Configure email (optional)
    # alerts_system.configure_email("smtp.gmail.com", 587, "your-email@gmail.com", "app-password")
    
    # Start monitoring
    await alerts_system.start_monitoring()
    
    # Create sample alerts
    user_id = "user123"
    
    # Price target alerts
    alert1 = await alerts_system.create_alert(
        user_id, "RELIANCE", AlertType.PRICE_ABOVE, 2600,
        [NotificationChannel.POPUP, NotificationChannel.EMAIL],
        message="RELIANCE hit target price!"
    )
    
    alert2 = await alerts_system.create_alert(
        user_id, "TCS", AlertType.PRICE_BELOW, 3000,
        [NotificationChannel.POPUP],
        message="TCS support level breached"
    )
    
    # Percentage alerts
    alert3 = await alerts_system.create_alert(
        user_id, "INFY", AlertType.PERCENTAGE_GAIN, 5,
        [NotificationChannel.EMAIL]
    )
    
    print(f"Created alerts: {alert1}, {alert2}, {alert3}")
    
    # Create smart alerts for portfolio
    sample_portfolio = {
        'stocks': [
            {'symbol': 'RELIANCE', 'current_price': 2500, 'purchase_price': 2300},
            {'symbol': 'TCS', 'current_price': 3200, 'purchase_price': 3000},
            {'symbol': 'INFY', 'current_price': 1400, 'purchase_price': 1200}
        ]
    }
    
    smart_alerts = await alerts_system.create_smart_alerts(user_id, sample_portfolio)
    print(f"Created smart alerts: {smart_alerts}")
    
    # Get active alerts
    active_alerts = alerts_system.get_active_alerts(user_id)
    print(f"Active alerts: {len(active_alerts)}")
    
    # Simulate some time passing for alerts to trigger
    print("Monitoring for alerts... (This would run continuously in production)")
    await asyncio.sleep(5)
    
    # Export alerts data
    alerts_json = alerts_system.export_alerts_to_json()
    print(f"Alerts data exported: {len(alerts_json)} characters")


if __name__ == "__main__":
    asyncio.run(test_price_alerts())